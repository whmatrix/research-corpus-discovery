# FAISS Index Construction

## Index Type: IndexFlatIP

The index uses FAISS `IndexFlatIP` (flat inner product), which performs exact nearest-neighbour search via brute-force inner product computation.

### Why IndexFlatIP

- **Exact search** - No approximation. Every query computes similarity against every vector. For corpora under ~100,000 vectors, this is fast enough (< 100ms query latency).
- **Cosine similarity via inner product** - Because all vectors are L2-normalised before indexing, inner product equals cosine similarity. This avoids the need for a separate normalisation step at query time.
- **No training required** - Unlike IVF or HNSW indexes, IndexFlatIP has no training phase. Vectors are added directly.
- **Deterministic** - Results are reproducible. The same query always returns the same results.

### When to Use a Different Index

For corpora exceeding ~100,000 vectors, consider:
- `IndexIVFFlat` - Partitioned search for faster queries (requires training)
- `IndexHNSWFlat` - Graph-based approximate search (faster for very large corpora)

The corpora tested here range from 563 to ~40,000 vectors, well within IndexFlatIP's performance envelope.

## Construction

```python
import faiss
import numpy as np

# Embeddings are already FP16 from the encoding step
embeddings_f32 = embeddings.astype(np.float32)

# Normalise for cosine similarity via inner product
faiss.normalize_L2(embeddings_f32)

# Build index
index = faiss.IndexFlatIP(1024)  # 1024-dimensional vectors
index.add(embeddings_f32)
```

## Serialisation

The index is written to disk with `faiss.write_index()` and loaded with `faiss.read_index()`. Index file sizes scale linearly with vector count:

| Vectors | Index Size |
|---------|-----------|
| 563 | ~2 MB |
| 1,919 | 7.5 MB |
| 8,339 | 34 MB |
| 8,902 | 35 MB |

## Alignment Verification

After building, the pipeline verifies that:

```
faiss_index.ntotal == len(chunks)
```

If this check fails, the index is misaligned and results will map to wrong chunks. The build script reports this in `index_report.json`.

## Querying

See [query.md](query.md) for the query pipeline.
