> **Author:** John Mitchell (@whmatrix)
> **Status:** ACTIVE
> **Audience:** Researchers / Applied ML
> **Environment:** GPU recommended (CPU fallback for queries)
> **Fast Path:** `python scripts/build_index.py --help`

# Semantic Search for Research Corpora

Build FAISS-indexed semantic search over document archives using e5-large-v2 embeddings.

Given a directory of PDFs, this tool extracts text, chunks it into overlapping passages, generates 1024-dimensional dense vector embeddings, and builds a FAISS index for fast cosine similarity search. Natural-language queries return the most relevant passages ranked by semantic similarity.

**Tested on 10 research institutions with 4,600+ documents.** Mean top-1 cosine similarity: 0.85. Query latency: < 100ms.

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
| Mean top-1 cosine similarity | 0.85 |
| Build time (8,000 chunks) | < 1 minute |
| Query latency | < 100ms |

See [case_studies/](case_studies/) for four detailed examples demonstrating cross-topic discovery, longitudinal concept tracking, comparative analysis, and small-team efficiency.

---

## Evaluation Method

### What the 0.85 Score Means

**Metric:** Mean top-1 inner product score (equivalent to cosine similarity on L2-normalized embeddings)

**How it was computed:**
1. **Evaluation set:** 50 queries constructed from known document topics (e.g., querying a known paper title against the corpus containing that paper)
2. **Procedure:** Each query was run against each institution's FAISS index. The inner product score of the rank-1 result was recorded.
3. **Aggregation:** Mean across all queries and institutions = **0.85**

**Conditions:**
| Parameter | Value |
|-----------|-------|
| Corpus | 4,600+ documents, 10 institutions, ~75,000 chunks |
| Embedding model | intfloat/e5-large-v2 (1024-dim, FP16) |
| Normalization | L2-normalized (so IP = cosine similarity) |
| Index type | FAISS IndexFlatIP (exact search, no approximation) |
| Score range | [0.0, 1.0] where 1.0 = identical embedding direction |

### What This Does NOT Claim

- **Not human-judged relevance.** The 0.85 is a vector similarity score, not a precision or recall metric. No labeled relevance judgments were collected.
- **Not MRR or MAP.** Those require binary relevance labels per result. This is a raw similarity score.
- **Not out-of-distribution.** Evaluation queries were constructed from known topics within the corpus. Performance on novel queries is untested.
- **Not cross-corpus.** Scores are meaningful within a single index. A 0.85 in a focused 45-document corpus is not comparable to 0.85 in a broad 1,621-document corpus.
- **Not a threshold.** Scores are useful for ranking, not for binary "relevant/not-relevant" decisions.

**Interpretation:** On average, the top-ranked chunk has an embedding that is 85% aligned with the query embedding. This indicates strong semantic retrieval within the indexed domain, but does not guarantee subjective relevance. See [methodology/query.md](methodology/query.md) for score interpretation and [results/benchmarks.md](results/benchmarks.md) for per-institution breakdowns.

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

## What You Get

| Deliverable | Format | Guarantee |
|-------------|--------|-----------|
| Vector index | FAISS IndexFlatIP (exact cosine via L2-normalized inner product) | Deterministic, byte-reproducible |
| Chunk corpus | JSONL with metadata | len(vectors) == len(chunks) == len(metadata) |
| Audit summary | JSON manifest | Pass/fail quality gates per Universal Protocol v4.23 |

**What this is not:** No human-judged relevance labels. No MRR/MAP/NDCG claims. Scores are cosine similarity (vector alignment), not precision or recall. Domain suitability requires independent evaluation.

**Reproduce it:** `git clone https://github.com/whmatrix/semantic-indexing-batch-02 && cd semantic-indexing-batch-02/mini-index && pip install sentence-transformers faiss-cpu && python demo_query.py`

---

## Non-Claims Statement

This tool indexes and retrieves documents based on semantic similarity. It does not interpret, summarise, or evaluate the content it returns. No claims are made about document quality, correctness, or completeness. The tool is not intended to replace domain expertise or human review. Similarity scores reflect vector alignment, not factual accuracy.

---

## Related Repositories

| Repository | Description |
|------------|-------------|
| [semantic-indexing-batch-02](https://github.com/whmatrix/semantic-indexing-batch-02) | Production indexing: 8.35M vectors across Wikipedia, ArXiv, StackExchange |
| [universal-protocol-v4.23](https://github.com/whmatrix/universal-protocol-v4.23) | Protocol specification for RAG deliverables and audit contracts |
| [whmatrix](https://github.com/whmatrix/whmatrix) | Portfolio hub and routing |
