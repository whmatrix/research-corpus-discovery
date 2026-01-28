#!/usr/bin/env python3
"""
Semantic Index Builder for Research Corpora

Builds a FAISS-indexed semantic search layer over a directory of PDF documents.
Uses intfloat/e5-large-v2 embeddings (1024-dim) with FP16 precision on GPU.

Usage:
    python build_index.py --pdf_dir ./pdfs --output_dir ./index

    # Custom chunking parameters
    python build_index.py --pdf_dir ./pdfs --output_dir ./index \
        --chunk_target 800 --chunk_overlap 100 --chunk_min 200

    # With a skip list for OCR-only PDFs
    python build_index.py --pdf_dir ./pdfs --output_dir ./index \
        --skip_list skip.txt

Output:
    output_dir/
    ├── faiss.index       FAISS IndexFlatIP vector index
    ├── chunks.jsonl      Chunk texts with metadata
    ├── metadata.jsonl    Document-level metadata
    └── index_report.json Build statistics and verification
"""

import sys
import json
import re
import hashlib
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

import numpy as np


# ── Invariants ───────────────────────────────────────────────────────────────

EMBEDDING_MODEL = "intfloat/e5-large-v2"
EMBEDDING_DIM = 1024
BATCH_SIZE = 1300
FP16 = True

# Section markers for academic / policy papers
SECTION_MARKERS = [
    r'^abstract\s*$',
    r'^introduction\s*$',
    r'^background\s*$',
    r'^literature\s+review\s*$',
    r'^data\s*$',
    r'^data\s+and\s+methods?\s*$',
    r'^methods?\s*$',
    r'^methodology\s*$',
    r'^model\s*$',
    r'^theoretical\s+framework\s*$',
    r'^empirical\s+(strategy|approach|analysis)\s*$',
    r'^results?\s*$',
    r'^findings?\s*$',
    r'^discussion\s*$',
    r'^conclusions?\s*$',
    r'^policy\s+implications?\s*$',
    r'^references?\s*$',
    r'^bibliography\s*$',
    r'^appendix\s*',
    r'^\d+\.\s+\w+',
]


# ── Text extraction ──────────────────────────────────────────────────────────

def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(8192), b''):
            sha256.update(block)
    return sha256.hexdigest()


def extract_text(pdf_path: Path) -> Tuple[str, int]:
    """Extract text from a PDF using pdftotext.

    Returns (text, page_count).
    """
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', str(pdf_path), '-'],
            capture_output=True, text=True, timeout=120
        )
        text = result.stdout
        page_count = text.count('\x0c') + 1 if text else 0
        return text, page_count
    except Exception as e:
        print(f"  ERROR extracting {pdf_path.name}: {e}")
        return "", 0


def parse_metadata(text: str, filename: str) -> Dict:
    """Extract basic metadata from the first page of PDF text."""
    first_page = text.split('\x0c')[0] if '\x0c' in text else text[:3000]
    metadata: Dict = {
        'title': '',
        'year': None,
        'doi': '',
    }

    # Year from text (4-digit year in a plausible range)
    year_match = re.search(r'\b(19[5-9]\d|20[0-2]\d)\b', first_page)
    if year_match:
        metadata['year'] = int(year_match.group(1))

    # DOI
    doi_match = re.search(r'(https?://doi\.org/[^\s]+|10\.\d{4,}/[^\s]+)', first_page)
    if doi_match:
        metadata['doi'] = doi_match.group(1)

    # Title heuristic: first substantial line after header boilerplate
    lines = first_page.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) > 20 and not re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', line):
            metadata['title'] = line[:200]
            break

    return metadata


# ── Chunking ─────────────────────────────────────────────────────────────────

def is_section_header(line: str) -> bool:
    """Check if a line matches a known section header pattern."""
    line_lower = line.strip().lower()
    return any(re.match(p, line_lower, re.I) for p in SECTION_MARKERS)


def chunk_text(text: str, target_tokens: int = 800,
               overlap_tokens: int = 100, min_tokens: int = 200) -> List[Dict]:
    """Section-aware chunking for academic / policy documents.

    Splits on paragraph boundaries, respects section headers,
    and maintains overlap between consecutive chunks.

    Token estimates use the approximation 1 token ~ 4 characters.
    """
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    paragraphs = text.split('\n\n')

    chunks: List[Dict] = []
    current_paras: List[str] = []
    current_tokens = 0
    current_section = "document"
    chunk_id = 0

    def _flush():
        nonlocal chunk_id, current_paras, current_tokens
        if current_tokens < min_tokens // 2:
            return
        chunk_text_str = '\n\n'.join(current_paras)
        chunks.append({
            'chunk_id': chunk_id,
            'text': chunk_text_str,
            'section': current_section,
            'char_count': len(chunk_text_str),
            'token_estimate': len(chunk_text_str) // 4,
        })
        chunk_id += 1

        # Keep overlap
        overlap_paras: List[str] = []
        overlap_size = 0
        for p in reversed(current_paras):
            p_tok = len(p) // 4
            if overlap_size + p_tok <= overlap_tokens:
                overlap_paras.insert(0, p)
                overlap_size += p_tok
            else:
                break
        current_paras = overlap_paras
        current_tokens = overlap_size

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_tokens = len(para) // 4
        first_line = para.split('\n')[0] if '\n' in para else para

        if is_section_header(first_line):
            if current_tokens >= min_tokens:
                _flush()
            current_section = first_line.strip()

        current_paras.append(para)
        current_tokens += para_tokens

        if current_tokens >= target_tokens:
            _flush()

    # Final chunk
    _flush()
    return chunks


# ── Embedding ────────────────────────────────────────────────────────────────

def generate_embeddings(chunks: List[Dict]) -> np.ndarray:
    """Generate e5-large-v2 embeddings on GPU.

    Requires CUDA. Uses FP16 precision to stay within a 3 GB VRAM envelope.
    """
    from sentence_transformers import SentenceTransformer
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA not available. GPU is required for embedding generation. "
            "Install a CUDA-capable PyTorch build or run on a machine with "
            "an NVIDIA GPU."
        )

    torch.cuda.empty_cache()
    device = 'cuda'

    print(f"Loading model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL, device=device)
    model.half()  # FP16

    texts = [f"passage: {c['text']}" for c in chunks]
    print(f"Embedding {len(texts)} chunks ...")

    with torch.no_grad():
        embeddings = model.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

    if FP16:
        embeddings = embeddings.astype(np.float16)

    print(f"Embeddings shape: {embeddings.shape}")
    return embeddings


# ── FAISS index ──────────────────────────────────────────────────────────────

def build_faiss_index(embeddings: np.ndarray):
    """Build a FAISS IndexFlatIP from L2-normalised embeddings.

    IndexFlatIP with normalised vectors is equivalent to cosine similarity.
    """
    import faiss

    embeddings_f32 = embeddings.astype(np.float32)
    faiss.normalize_L2(embeddings_f32)

    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(embeddings_f32)

    print(f"FAISS index: {index.ntotal} vectors")
    return index


# ── I/O ──────────────────────────────────────────────────────────────────────

def save_outputs(output_dir: Path, chunks, metadata, embeddings, index, stats):
    """Write all build artifacts to *output_dir*."""
    import faiss

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().isoformat() + 'Z'

    # chunks.jsonl
    chunks_path = output_dir / "chunks.jsonl"
    with open(chunks_path, 'w') as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + '\n')
    print(f"Saved: {chunks_path}")

    # metadata.jsonl
    metadata_path = output_dir / "metadata.jsonl"
    with open(metadata_path, 'w') as f:
        for doc in metadata:
            f.write(json.dumps(doc) + '\n')
    print(f"Saved: {metadata_path}")

    # FAISS index
    index_path = output_dir / "faiss.index"
    faiss.write_index(index, str(index_path))
    print(f"Saved: {index_path}")

    # Embeddings backup
    embeddings_path = output_dir / "embeddings.npy"
    np.save(embeddings_path, embeddings)
    print(f"Saved: {embeddings_path}")

    # Report
    report = {
        'build_timestamp': timestamp,
        'embedding_model': EMBEDDING_MODEL,
        'embedding_dim': EMBEDDING_DIM,
        'fp16': FP16,
        'batch_size': BATCH_SIZE,
        'stats': {
            'pdf_count': stats['total_pdfs'],
            'docs_indexed': stats['processed'],
            'chunk_count': stats['total_chunks'],
            'faiss_ntotal': index.ntotal,
            'empty_text_docs': stats['empty_text'],
            'low_text_docs': stats['low_text'],
        },
        'integrity': {
            'alignment_verified': index.ntotal == len(chunks),
        },
        'extraction_quality': {
            'empty_text_pct': round(100 * stats['empty_text'] / max(stats['total_pdfs'], 1), 2),
            'low_text_pct': round(100 * stats['low_text'] / max(stats['total_pdfs'], 1), 2),
        },
    }

    report_path = output_dir / "index_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Saved: {report_path}")

    return report


# ── Pipeline ─────────────────────────────────────────────────────────────────

def process_pdfs(pdf_dir: Path, skip_set: set,
                 chunk_target: int, chunk_overlap: int, chunk_min: int):
    """Extract text from all PDFs, chunk, and collect metadata."""
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdfs)} PDFs in {pdf_dir}")

    all_chunks: List[Dict] = []
    all_metadata: List[Dict] = []
    stats = {
        'total_pdfs': len(pdfs),
        'processed': 0,
        'empty_text': 0,
        'low_text': 0,
        'total_chunks': 0,
    }

    for i, pdf_path in enumerate(pdfs):
        if pdf_path.name in skip_set:
            print(f"[{i+1}/{len(pdfs)}] Skipping (skip list): {pdf_path.name}")
            continue

        if i % 50 == 0:
            print(f"[{i+1}/{len(pdfs)}] Processing: {pdf_path.name}")

        doc_id = pdf_path.stem
        text, page_count = extract_text(pdf_path)
        meta = parse_metadata(text, pdf_path.name)
        meta['doc_id'] = doc_id
        meta['filename'] = pdf_path.name
        meta['sha256'] = compute_sha256(pdf_path)
        meta['bytes'] = pdf_path.stat().st_size
        meta['pages'] = page_count

        text_len = len(text.strip())
        if text_len < 100:
            stats['empty_text'] += 1
            meta['extraction_quality'] = 'empty'
        elif text_len < 1000:
            stats['low_text'] += 1
            meta['extraction_quality'] = 'low'
        else:
            meta['extraction_quality'] = 'ok'

        if text_len >= 100:
            chunks = chunk_text(text, chunk_target, chunk_overlap, chunk_min)
            for chunk in chunks:
                chunk['doc_id'] = doc_id
                chunk['filename'] = pdf_path.name
                chunk['title'] = meta.get('title', '')
                chunk['year'] = meta.get('year')
                all_chunks.append(chunk)
            meta['chunk_count'] = len(chunks)
            stats['total_chunks'] += len(chunks)
        else:
            meta['chunk_count'] = 0

        all_metadata.append(meta)
        stats['processed'] += 1

    return all_chunks, all_metadata, stats


def main():
    parser = argparse.ArgumentParser(
        description='Build a FAISS semantic search index over a PDF corpus.'
    )
    parser.add_argument('--pdf_dir', required=True,
                        help='Directory containing PDF files')
    parser.add_argument('--output_dir', required=True,
                        help='Directory to write index artifacts')
    parser.add_argument('--chunk_target', type=int, default=800,
                        help='Target chunk size in tokens (default: 800)')
    parser.add_argument('--chunk_overlap', type=int, default=100,
                        help='Overlap between chunks in tokens (default: 100)')
    parser.add_argument('--chunk_min', type=int, default=200,
                        help='Minimum chunk size in tokens (default: 200)')
    parser.add_argument('--skip_list',
                        help='File listing PDF filenames to skip (one per line)')
    args = parser.parse_args()

    pdf_dir = Path(args.pdf_dir)
    output_dir = Path(args.output_dir)

    if not pdf_dir.is_dir():
        print(f"ERROR: PDF directory not found: {pdf_dir}")
        sys.exit(1)

    skip_set: set = set()
    if args.skip_list:
        skip_path = Path(args.skip_list)
        if skip_path.exists():
            skip_set = {
                line.strip() for line in skip_path.read_text().splitlines()
                if line.strip()
            }
            print(f"Skip list: {len(skip_set)} files")

    print("=" * 60)
    print("Semantic Index Builder")
    print(f"  PDF directory : {pdf_dir}")
    print(f"  Output        : {output_dir}")
    print(f"  Chunk target  : {args.chunk_target} tokens")
    print(f"  Chunk overlap : {args.chunk_overlap} tokens")
    print(f"  Chunk minimum : {args.chunk_min} tokens")
    print("=" * 60)

    # Step 1: Extract and chunk
    print("\n[1/4] Extracting and chunking PDFs ...")
    chunks, metadata, stats = process_pdfs(
        pdf_dir, skip_set,
        args.chunk_target, args.chunk_overlap, args.chunk_min
    )
    print(f"  {len(chunks)} chunks from {stats['processed']} documents")

    if not chunks:
        print("ERROR: No chunks produced. Check PDF directory and extraction.")
        sys.exit(1)

    # Step 2: Embed
    print("\n[2/4] Generating embeddings ...")
    embeddings = generate_embeddings(chunks)

    # Step 3: Build FAISS index
    print("\n[3/4] Building FAISS index ...")
    index = build_faiss_index(embeddings)

    # Step 4: Save
    print("\n[4/4] Saving outputs ...")
    report = save_outputs(output_dir, chunks, metadata, embeddings, index, stats)

    aligned = report['integrity']['alignment_verified']
    print("\n" + "=" * 60)
    print(f"BUILD {'COMPLETE' if aligned else 'COMPLETE (alignment warning)'}")
    print(f"  Chunks  : {stats['total_chunks']}")
    print(f"  Vectors : {index.ntotal}")
    print(f"  Aligned : {aligned}")
    print("=" * 60)


if __name__ == '__main__':
    main()
