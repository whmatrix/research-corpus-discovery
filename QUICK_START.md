# Quick Start: Build and Query a Semantic Index

Build a small semantic index from sample documents and run queries against it.

## Prerequisites

```bash
# System dependency
sudo apt install poppler-utils   # provides pdftotext

# Python dependencies
pip install -r scripts/requirements.txt
```

Requires an NVIDIA GPU with CUDA for index building. Querying supports CPU fallback.

## Step 1: Build an Index from Sample Documents

```bash
python scripts/build_index.py \
    --pdf_dir ./sample_docs/ \
    --output_dir ./demo_index
```

**What this does:**
1. Extracts text from each PDF via `pdftotext`
2. Splits text into overlapping chunks (~800 tokens each, section-aware)
3. Embeds each chunk with `intfloat/e5-large-v2` (1024-dim, FP16, GPU)
4. Builds a FAISS `IndexFlatIP` for exact cosine similarity search
5. Writes all artifacts to `./demo_index/`

**Output:**
```
demo_index/
├── faiss.index          FAISS vector index
├── chunks.jsonl         Chunk texts with metadata
├── metadata.jsonl       Document-level metadata
├── embeddings.npy       Raw embedding vectors
└── index_report.json    Build statistics and integrity check
```

With the sample documents included in this repo, the build produces ~50-80 chunks.

---

## Step 2: Run Queries

### Single query

```bash
python scripts/query.py \
    --index ./demo_index/faiss.index \
    --chunks ./demo_index/chunks.jsonl \
    --query "how do institutional frameworks affect policy outcomes"
```

### Interactive mode

```bash
python scripts/query.py \
    --index ./demo_index/faiss.index \
    --chunks ./demo_index/chunks.jsonl
```

### JSON output

```bash
python scripts/query.py \
    --index ./demo_index/faiss.index \
    --chunks ./demo_index/chunks.jsonl \
    --query "cross-disciplinary approaches to labor economics" \
    --json
```

**Try these queries:**

```
> how do institutional frameworks affect policy outcomes
> cross-disciplinary approaches to labor economics
> environmental policy and regional economic effects
> migration patterns and workforce demographics
> research methodology for longitudinal studies
```

---

## Step 3: Understand the Output

Each result shows:

```
============================================================
[1]  Score: 0.8472
  Document : institutional_economics_working_paper
  Title    : Institutional Frameworks and Regional Policy Outcomes
  Year     : 2023
  Section  : Empirical Analysis

  The relationship between institutional design and policy outcomes has been
  studied extensively in the comparative politics literature. Our analysis
  extends this framework to regional economic development ...
```

- **Score**: Cosine similarity (0.0-1.0). Higher = more semantically relevant.
- **Document**: Source PDF filename (minus extension).
- **Section**: Which section of the document the chunk came from.
- **Snippet**: First 300 characters of the matched chunk.

Scores are relative to the corpus. A score of 0.85 in a focused corpus and 0.85 in a broad corpus reflect different levels of specificity.

---

## Variations

**Index your own PDFs:**

```bash
python scripts/build_index.py \
    --pdf_dir /path/to/your/pdfs/ \
    --output_dir ./my_index
```

**Adjust chunking:**

```bash
python scripts/build_index.py \
    --pdf_dir ./pdfs \
    --output_dir ./index \
    --chunk_target 600 \
    --chunk_overlap 75 \
    --chunk_min 150
```

**Skip problematic PDFs:**

```bash
echo "scanned_only.pdf" > skip.txt
python scripts/build_index.py \
    --pdf_dir ./pdfs \
    --output_dir ./index \
    --skip_list skip.txt
```

---

## What This Demonstrates

- The pipeline is reproducible (run it yourself on any PDF corpus)
- Semantic search returns meaningful results ranked by relevance
- Section-aware chunking preserves document structure
- Asymmetric encoding (`query:` / `passage:` prefixes) improves retrieval
- Build artifacts are self-documenting (`index_report.json` includes integrity checks)

---

## Next Steps

- `README.md` — Full project documentation and proof-of-concept statistics
- `case_studies/` — How 10 institutions used this pipeline
- `methodology/` — Detailed documentation of each pipeline stage
- `demo/sample_queries.md` — 10 curated queries with scores from real corpora
