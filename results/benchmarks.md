# Benchmarks: 10 Corpora

Aggregate statistics from semantic index builds across 10 research organizations.

---

## 1. Corpus Statistics

| Metric | Value |
|--------|-------|
| Organizations tested | 10 |
| Total documents | ~4,600 |
| Total chunks (estimated) | ~75,000 |
| Smallest corpus | 45 documents, 563 chunks |
| Largest corpus | 1,621 documents, ~40,000 chunks |
| Document type | PDF (all) |
| Language | English |
| Date range | 1900-2025 |

### Per-Organization Breakdown

| Org (Anonymised) | Documents | Chunks | Time Span | Domain |
|-------------------|-----------|--------|-----------|--------|
| Regional Think Tank | 178 | 8,339 | 2000-2025 | Regional economics |
| Policy Research Lab | 102 | 2,760 | 2015-2025 | Multi-sector policy |
| Australian Policy Institute | 284 | 8,902 | 2009-2025 | Public policy |
| Foreign Policy Center | 142 | 1,919 | 2019-2025 | Foreign policy |
| Labor Economics Archive | 413 | ~7,500 | 1990-2025 | Labor economics |
| Legacy Economics Archive | 1,621 | ~40,000 | 1900-2025 | Economics |
| Migration Research Institute | 45 | 563 | 2001-2025 | Migration policy |
| Water Policy Institute | 691 | ~12,000 | 2000-2025 | Water & environment |
| Progressive Policy Institute | 629 | ~11,000 | 2010-2025 | Progressive policy |
| State Economic Research Center | 251 | ~5,000 | 2005-2025 | State economics |

---

## 2. Build Configuration (Invariant)

| Parameter | Value |
|-----------|-------|
| Embedding model | intfloat/e5-large-v2 |
| Embedding dimension | 1024 |
| Precision | FP16 |
| FAISS index type | IndexFlatIP |
| Query prefix | `query: ` |
| Passage prefix | `passage: ` |
| Normalisation | L2 (cosine via inner product) |

### Chunking Parameters (Varied by Corpus)

| Corpus Type | Target | Overlap | Min |
|-------------|--------|---------|-----|
| Academic papers | 800 tokens | 100 tokens | 200 tokens |
| Policy briefs | 800-1000 tokens | 100-150 tokens | 100-200 tokens |
| Structured reports | 512 tokens | 64 tokens | 100 tokens |
| Large documents | 1000 tokens | 150 tokens | 200 tokens |

---

## 3. Cosine Similarity Distributions

Across all demo queries from all 10 organizations:

| Score Range | % of Top-1 Results | Interpretation |
|-------------|-------------------|----------------|
| 0.85 - 1.00 | 45% | Strong match |
| 0.80 - 0.85 | 40% | Good match |
| 0.75 - 0.80 | 10% | Moderate match |
| < 0.75 | 5% | Weak match |

### Per-Organization Mean Top-1 Scores

| Organisation | Avg Top-1 Score | Queries Tested |
|-------------|----------------|----------------|
| Policy Research Lab | 0.87 | 10 |
| Labor Economics Archive | 0.87+ | 10 |
| Foreign Policy Center | 0.84 | 10 |
| Regional Think Tank | 0.84 | 8 |
| Australian Policy Institute | ~0.83 | 8 |
| Migration Research Institute | N/A (qualitative) | 5 |

**Overall average:** 0.85 across all scored queries.

---

## 4. Build Performance

All builds on NVIDIA RTX A6000 (48 GB VRAM). Peak VRAM usage < 3 GB in all cases.

| Corpus | Chunks | Embedding Time | Throughput | Index Size |
|--------|--------|---------------|------------|-----------|
| Regional Think Tank | 8,339 | 43s | 194 chunks/s | 34 MB |
| Foreign Policy Center | 1,919 | 11.2s | 171 chunks/s | 7.5 MB |
| Australian Policy Institute | 8,902 | 50s | 87 chunks/s | 35 MB |

### Derived Estimates

| Corpus Size | Est. Embedding Time | Est. Index Size |
|------------|-------------------|----------------|
| 1,000 chunks | ~6 seconds | ~4 MB |
| 5,000 chunks | ~30 seconds | ~20 MB |
| 10,000 chunks | ~60 seconds | ~40 MB |
| 50,000 chunks | ~5 minutes | ~200 MB |

Query latency: **< 100ms** for all tested corpora (up to ~40,000 vectors with IndexFlatIP).

---

## 5. Extraction Quality

| Metric | Range Across 10 Orgs |
|--------|---------------------|
| Extraction success rate | 98.9% - 100% |
| Empty text (< 100 chars) | 0% - 1.1% |
| Low text (100-1000 chars) | 0% - 2% |
| OCR-required (deferred) | 0-2 documents per org |

Most PDFs from research organizations have native text layers and extract cleanly. The few failures are scanned documents (charts, reports from the 1990s-2000s).

---

## 6. Query Patterns

### Query Types That Work Well

| Pattern | Example | Why It Works |
|---------|---------|-------------|
| Cross-topic discovery | "How does food assistance eligibility affect college students?" | Connects two topic silos |
| Longitudinal tracking | "How has unemployment research evolved?" | Retrieves across decades |
| Cross-regional comparison | "What coordination failures exist in both U.S. and EU systems?" | Finds structural parallels |
| Buried recommendations | "What institutional adaptations are recommended?" | Surfaces conclusion sections |
| Specific program evaluation | "What is the impact of place-based scholarships?" | Retrieves multiple evaluations |

### Query Types That Struggle

| Pattern | Example | Why It Struggles |
|---------|---------|-----------------|
| Very broad | "economics" | Returns everything, nothing useful |
| Named entity lookup | "What did Smith write?" | Semantic search isn't author search |
| Exact citation | "Table 3 results" | Positional references don't embed well |
| Numerical queries | "GDP growth rate 2019" | Numbers lose precision in embeddings |
