# Semantic Search for Research Corpora

Build FAISS-indexed semantic search over document archives using e5-large-v2 embeddings.

Given a directory of PDFs, this tool extracts text, chunks it into overlapping passages, generates 1024-dimensional dense vector embeddings, and builds a FAISS index for fast cosine similarity search. Natural-language queries return the most relevant passages ranked by semantic similarity.

**Tested on 10 research institutions with 4,600+ documents.** Average top-1 relevance score: 0.85. Query latency: < 100ms.

---

## Quick Start

### Build an index

```bash
python scripts/build_index.py \
    --pdf_dir ./pdfs \
    --output_dir ./index
```

### Query the index

```bash
python scripts/query.py \
    --index ./index/faiss.index \
    --chunks ./index/chunks.jsonl \
    --query "your question here"
```

### Interactive mode

```bash
python scripts/query.py \
    --index ./index/faiss.index \
    --chunks ./index/chunks.jsonl
```

---

## Requirements

- Python 3.9+
- NVIDIA GPU with CUDA (required for index building; query supports CPU fallback)
- `pdftotext` from the Poppler library (`apt install poppler-utils` or `brew install poppler`)

```bash
pip install -r scripts/requirements.txt
```

---

## How It Works

1. **Extract** - PDF text extraction via `pdftotext` with layout preservation
2. **Chunk** - Section-aware splitting with configurable token targets and overlap
3. **Embed** - `intfloat/e5-large-v2` dense vectors at FP16 precision
4. **Index** - FAISS `IndexFlatIP` for exact cosine similarity search
5. **Query** - Asymmetric encoding (`query:` / `passage:` prefixes) for retrieval-optimised results

See [methodology/](methodology/) for detailed documentation of each stage.

---

## Proof of Concept

This pipeline was tested on 10 policy and economics research organizations:

| Metric | Value |
|--------|-------|
| Organizations | 10 |
| Total documents | ~4,600 |
| Total chunks | ~75,000 |
| Corpora range | 45 - 1,621 documents |
| Time span | 1900 - 2025 |
| Domains | Economics, policy, migration, labor, environment, foreign policy |
| Average top-1 score | 0.85 |
| Build time (8,000 chunks) | < 1 minute |
| Query latency | < 100ms |

See [case_studies/](case_studies/) for four detailed examples demonstrating cross-topic discovery, longitudinal concept tracking, comparative analysis, and small-team efficiency.

---

## Repository Structure

```
research-corpus-discovery/
├── README.md
├── scripts/
│   ├── build_index.py          Build a FAISS index from PDFs
│   ├── query.py                Query an existing index
│   └── requirements.txt        Python dependencies
├── methodology/
│   ├── overview.md             Pipeline summary
│   ├── acquire.md              PDF collection methods
│   ├── chunk_and_embed.md      Chunking strategy and embedding model
│   ├── index.md                FAISS index construction
│   └── query.md                Query pipeline and score interpretation
├── case_studies/
│   ├── overview.md             Summary of all 10 tested corpora
│   ├── legacy_economics_archive.md     125-year archive (1,621 docs)
│   ├── policy_research_lab.md          Cross-topic discovery (102 docs)
│   ├── migration_research_institute.md Persona-driven queries (45 docs)
│   └── regional_think_tank.md          Multi-topic synthesis (178 docs)
├── demo/
│   ├── sample_queries.md       10 best queries across all corpora
│   └── sample_output.md        Example terminal output
└── results/
    └── benchmarks.md           Aggregate statistics across 10 orgs
```

---

## Build Parameters

| Parameter | Default | Flag |
|-----------|---------|------|
| Chunk target | 800 tokens | `--chunk_target` |
| Chunk overlap | 100 tokens | `--chunk_overlap` |
| Chunk minimum | 200 tokens | `--chunk_min` |
| Skip list | None | `--skip_list` |

The embedding model (`intfloat/e5-large-v2`), dimension (1024), and index type (`IndexFlatIP`) are fixed. These produced consistent results across all tested corpora and are not intended to be changed without re-evaluating retrieval quality.

---

## Use Cases

- **Document discovery for researchers** - Find relevant prior work across large archives without knowing exact titles or keywords
- **Cross-topic search** - Surface connections between work filed under different topic categories
- **Historical trend discovery** - Trace how a concept was studied across decades of publications
- **Institutional memory** - Enable new team members to query an organization's full research history
- **Literature review acceleration** - Locate all relevant passages on a topic across hundreds of documents

---

## Limitations

- Requires native text layers in PDFs. Scanned documents need OCR preprocessing (not included).
- Section detection uses heuristic pattern matching. Non-standard section headers may not be recognized.
- Score interpretation is relative to the corpus. A score of 0.80 in a focused corpus means something different than 0.80 in a broad one.
- Embedding quality depends on the model. Results may differ for non-English text or highly technical notation.
- IndexFlatIP performs exact search. For corpora exceeding ~100,000 vectors, an approximate index (IVF, HNSW) would be faster.

---

## Non-Claims Statement

This tool indexes and retrieves documents based on semantic similarity. It does not interpret, summarise, or evaluate the content it returns. No claims are made about document quality, correctness, or completeness. The tool is not intended to replace domain expertise or human review. Relevance scores reflect vector similarity, not factual accuracy.

---

## Related Repositories

| Repository | Description |
|------------|-------------|
| [semantic-indexing-batch-02](https://github.com/whmatrix/semantic-indexing-batch-02) | Production indexing: 8.35M vectors across Wikipedia, ArXiv, StackExchange |
| [universal-protocol-v4.23](https://github.com/whmatrix/universal-protocol-v4.23) | Protocol specification for RAG deliverables and audit contracts |
| [whmatrix](https://github.com/whmatrix/whmatrix) | Portfolio hub and routing |
