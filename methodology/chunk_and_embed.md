# Chunking and Embedding

## Text Extraction

PDFs are converted to plain text using `pdftotext` (from the Poppler library) with the `-layout` flag, which preserves spatial positioning. Page boundaries are detected via form feed characters (`\x0c`).

Files with fewer than 100 characters of extracted text are flagged as `empty` and excluded from chunking. Files with 100-1000 characters are flagged as `low` quality but still processed.

## Chunking Strategy

The chunking approach is section-aware and paragraph-respecting:

1. **Normalize whitespace** - Collapse runs of 3+ newlines to paragraph breaks; collapse horizontal whitespace
2. **Split on paragraphs** - Use double-newline as the primary boundary
3. **Detect section headers** - Recognise patterns like "Introduction", "Results", "1. Background", etc.
4. **Accumulate paragraphs** into chunks until the target token count is reached
5. **Flush on section boundary** - When a section header is encountered, the current chunk is saved (if it meets minimum size) and a new chunk begins
6. **Maintain overlap** - After flushing, the last N tokens of paragraphs carry over into the next chunk

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chunk_target` | 800 tokens | Target chunk size before flushing |
| `chunk_overlap` | 100 tokens | Tokens carried over between chunks |
| `chunk_min` | 200 tokens | Minimum chunk size to save |

Token estimation uses the approximation **1 token ~ 4 characters**, which is sufficiently accurate for English text with the e5 tokenizer.

### Why These Defaults

- **800 tokens** is large enough to capture a complete argument or finding, but small enough for precise retrieval. Larger chunks (1000+) dilute relevance; smaller chunks (< 400) lose context.
- **100-token overlap** ensures that a passage split across two chunks is still retrievable from either one.
- **200-token minimum** prevents tiny fragments (headers, table captions) from becoming standalone chunks.

These parameters are configurable via command-line arguments. In practice, values between 500-1000 tokens for the target work well across different document types (academic papers, policy briefs, reports).

### Section Markers

The chunker recognises these patterns as section boundaries:

```
Abstract, Introduction, Background, Literature Review,
Data, Data and Methods, Methods, Methodology, Model,
Theoretical Framework, Empirical Strategy/Approach/Analysis,
Results, Findings, Discussion, Conclusions, Policy Implications,
References, Bibliography, Appendix, Numbered sections (e.g., "1. Background")
```

When a section header is encountered, the current chunk is flushed (if large enough) and the new chunk begins with the header's section label as metadata.

## Embedding Model

**Model:** `intfloat/e5-large-v2`
**Dimensions:** 1024
**Precision:** FP16

### Why e5-large-v2

- State-of-the-art dense retrieval performance on MTEB benchmarks at the time of testing
- Asymmetric query/passage encoding: queries are prefixed with `"query: "` and passages with `"passage: "`, which improves retrieval quality for search-style workloads
- 1024-dimensional vectors provide enough capacity for nuanced semantic distinctions across large corpora
- Well-supported in the `sentence-transformers` library

### Encoding Details

- All passage texts are prefixed with `"passage: "` before encoding
- Embeddings are L2-normalised, so inner product equals cosine similarity
- FP16 precision halves VRAM usage (~1.5 GB model footprint vs. ~3 GB in FP32)
- Batch size of 1,300 keeps peak VRAM under 3 GB on a 48 GB GPU

### GPU Requirement

Embedding generation requires CUDA. The build script blocks if no GPU is available. On an NVIDIA RTX A6000:
- 1,919 chunks: 11 seconds (171 chunks/sec)
- 8,339 chunks: 43 seconds (194 chunks/sec)
- 8,902 chunks: 50 seconds (87 chunks/sec, I/O bound on larger documents)

## Output

Each chunk is stored as a JSON object in `chunks.jsonl` with:

```json
{
  "chunk_id": 0,
  "text": "The extracted passage text...",
  "section": "Introduction",
  "char_count": 3200,
  "token_estimate": 800,
  "doc_id": "document_stem",
  "filename": "document.pdf",
  "title": "Extracted Title",
  "year": 2020
}
```
