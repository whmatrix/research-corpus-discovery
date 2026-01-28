#!/usr/bin/env python3
"""
Semantic Search Query Tool

Query a FAISS index built by build_index.py. Returns the top-k most
semantically similar chunks with relevance scores and metadata.

Usage:
    # Single query
    python query.py --index ./index/faiss.index \
                    --chunks ./index/chunks.jsonl \
                    --query "minimum wage effects on employment"

    # Interactive mode (omit --query)
    python query.py --index ./index/faiss.index \
                    --chunks ./index/chunks.jsonl

    # JSON output
    python query.py --index ./index/faiss.index \
                    --chunks ./index/chunks.jsonl \
                    --query "unemployment insurance adequacy" \
                    --json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict

import numpy as np
import faiss


MODEL_NAME = "intfloat/e5-large-v2"


def load_index(index_path: Path, chunks_path: Path):
    """Load a FAISS index and its corresponding chunk metadata."""
    print("Loading index ...", file=sys.stderr)
    index = faiss.read_index(str(index_path))

    chunks: List[Dict] = []
    with open(chunks_path, 'r') as f:
        for line in f:
            chunks.append(json.loads(line))

    if index.ntotal != len(chunks):
        print(
            f"WARNING: index has {index.ntotal} vectors but chunks.jsonl "
            f"has {len(chunks)} entries",
            file=sys.stderr
        )

    return index, chunks


def load_model():
    """Load the embedding model (GPU if available, else CPU)."""
    from sentence_transformers import SentenceTransformer
    import torch

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Loading model on {device} ...", file=sys.stderr)
    model = SentenceTransformer(MODEL_NAME, device=device)
    if device == 'cuda':
        model.half()
    return model


def search(query: str, index, chunks: List[Dict], model,
           top_k: int = 5) -> List[Dict]:
    """Encode *query* and return the top-k matching chunks."""
    import torch

    query_text = f"query: {query}"
    with torch.no_grad():
        query_vec = model.encode(
            [query_text],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
    query_vec = query_vec.astype(np.float32)

    scores, indices = index.search(query_vec, top_k)

    results: List[Dict] = []
    for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), start=1):
        if idx < 0 or idx >= len(chunks):
            continue
        chunk = chunks[idx]
        text = chunk.get('text', '')
        results.append({
            'rank': rank,
            'score': round(float(score), 4),
            'doc_id': chunk.get('doc_id', ''),
            'title': chunk.get('title', 'Untitled'),
            'year': chunk.get('year'),
            'section': chunk.get('section', ''),
            'snippet': text[:300] + ' ...' if len(text) > 300 else text,
        })

    return results


def format_results(query: str, results: List[Dict]) -> str:
    """Format search results for terminal display."""
    lines = [
        f"\nQuery: {query}",
        f"Results: {len(results)}",
    ]
    for r in results:
        lines.append(f"\n{'=' * 60}")
        lines.append(f"[{r['rank']}]  Score: {r['score']}")
        lines.append(f"  Document : {r['doc_id']}")
        if r['title']:
            lines.append(f"  Title    : {r['title']}")
        if r['year']:
            lines.append(f"  Year     : {r['year']}")
        if r['section']:
            lines.append(f"  Section  : {r['section']}")
        lines.append(f"\n  {r['snippet']}")
    lines.append("")
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Query a FAISS semantic search index.'
    )
    parser.add_argument('--index', required=True,
                        help='Path to faiss.index file')
    parser.add_argument('--chunks', required=True,
                        help='Path to chunks.jsonl file')
    parser.add_argument('--query', '-q',
                        help='Search query (omit for interactive mode)')
    parser.add_argument('--top-k', '-k', type=int, default=5,
                        help='Number of results (default: 5)')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')
    args = parser.parse_args()

    index, chunks = load_index(Path(args.index), Path(args.chunks))
    model = load_model()

    if args.query:
        results = search(args.query, index, chunks, model, args.top_k)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(format_results(args.query, results))
    else:
        # Interactive mode
        print(f"\nSemantic Search  ({len(chunks)} chunks indexed)")
        print("Enter queries below. Ctrl+C to exit.\n")
        while True:
            try:
                query = input("Query: ").strip()
                if not query:
                    continue
                results = search(query, index, chunks, model, args.top_k)
                if args.json:
                    print(json.dumps(results, indent=2))
                else:
                    print(format_results(query, results))
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                break


if __name__ == '__main__':
    main()
