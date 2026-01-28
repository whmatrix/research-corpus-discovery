# Methodology Overview

This tool builds a semantic search layer over document archives. Given a directory of PDFs, it extracts text, splits it into overlapping chunks, generates dense vector embeddings, and indexes them for fast cosine similarity search. The result is a queryable index where natural-language questions return the most relevant document passages, ranked by semantic similarity.

The pipeline has four stages:

1. **[Acquire](acquire.md)** - Collect PDFs from the target corpus
2. **[Chunk & Embed](chunk_and_embed.md)** - Extract text, split into chunks, generate vector embeddings
3. **[Index](index.md)** - Build a FAISS vector index for fast retrieval
4. **[Query](query.md)** - Search the index with natural-language queries

Each stage is designed to be deterministic and verifiable. Alignment checks confirm that the number of chunks equals the number of vectors in the final index.
