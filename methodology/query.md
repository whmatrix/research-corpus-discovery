# Query Pipeline

## Overview

A query is encoded into the same vector space as the indexed passages, then compared against all stored vectors using cosine similarity (via inner product on normalised vectors). The top-k most similar chunks are returned with their metadata.

## Query Encoding

Queries use the `"query: "` prefix required by the e5 model's asymmetric encoding:

```python
query_text = f"query: {query}"
query_vec = model.encode(
    [query_text],
    normalize_embeddings=True,
    convert_to_numpy=True,
)
query_vec = query_vec.astype(np.float32)
```

The `"query: "` prefix tells the model this is a search query (short, question-like) rather than a passage (long, informational). This asymmetry improves retrieval quality compared to encoding both sides identically.

## Search

```python
scores, indices = index.search(query_vec, top_k)
```

FAISS returns:
- `scores` - Cosine similarity values (higher is more relevant, range 0-1 for normalised vectors)
- `indices` - Positions into the chunks array

## Result Assembly

Each result maps back to the original chunk metadata:

```python
{
    "rank": 1,
    "score": 0.861,
    "doc_id": "document_stem",
    "title": "Extracted Document Title",
    "year": 2020,
    "section": "Results",
    "snippet": "First 300 characters of the chunk text ..."
}
```

## Score Interpretation

| Score Range | Interpretation |
|-------------|---------------|
| 0.85 - 1.00 | Strong match. The passage directly addresses the query. |
| 0.75 - 0.85 | Good match. The passage is relevant, possibly from an adjacent section. |
| 0.65 - 0.75 | Moderate match. Related topic but may not directly answer the query. |
| < 0.65 | Weak match. Likely tangential or only keyword-adjacent. |

Across 10 tested corpora, average top-1 scores ranged from 0.82 to 0.89. Scores below 0.70 for a top-1 result usually indicate the query topic is not well-represented in the corpus.

## Query Design

Effective queries for research corpora tend to be:

- **Conceptual rather than keyword-based** - "How does minimum wage affect employment?" retrieves better than "minimum wage employment"
- **Specific enough to disambiguate** - "What workforce development strategies address skills gaps?" outperforms "workforce"
- **Cross-cutting for maximum value** - The strongest demonstration queries span multiple topics or time periods, surfacing connections invisible to browse-based interfaces

## Usage

```bash
# Single query
python scripts/query.py \
    --index ./index/faiss.index \
    --chunks ./index/chunks.jsonl \
    --query "unemployment insurance benefit adequacy" \
    -k 5

# Interactive mode
python scripts/query.py \
    --index ./index/faiss.index \
    --chunks ./index/chunks.jsonl

# JSON output
python scripts/query.py \
    --index ./index/faiss.index \
    --chunks ./index/chunks.jsonl \
    --query "your query" \
    --json
```
