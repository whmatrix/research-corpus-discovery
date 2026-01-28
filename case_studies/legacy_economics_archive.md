# Case Study: Legacy Economics Archive

**Domain:** Economics working papers
**Corpus:** 1,621 documents spanning 1900-2025
**Challenge:** Discovering research across a 125-year archive

---

## Problem

A longstanding economics research institute maintains one of the largest working paper archives in its field, covering 125 years of economic research. The archive includes working papers, policy notes, public policy briefs, one-pagers, and strategic analyses organized by series and publication number.

Researchers accessing this archive face a fundamental navigation problem: papers are browsable by year and series, but there is no way to trace a concept (e.g., "financial instability") across decades of publications. A researcher studying Modern Monetary Theory implications would need to manually scan thousands of titles to find relevant historical antecedents.

---

## Solution

A semantic search index was built over all 1,621 documents using the standard pipeline:

| Parameter | Value |
|-----------|-------|
| Documents | 1,621 PDFs |
| Chunking | 512 tokens target, 64-token overlap |
| Embedding | intfloat/e5-large-v2, FP16, 1024-dim |
| Index | FAISS IndexFlatIP |
| Architecture | Streaming with vector sharding (10,000 vectors/shard) |

The streaming architecture was necessary due to corpus size. A bounded producer-consumer queue processed PDFs in parallel with embedding generation, and RAM monitoring paused extraction when memory pressure exceeded 90%.

---

## Results

**Example queries and their retrieval behavior:**

| Query | Documents Retrieved | Time Span Covered |
|-------|-------|------|
| "financial instability hypothesis" | 15+ papers across 4 decades | 1985-2022 |
| "employer of last resort policy proposals" | 8+ papers | 1998-2020 |
| "trade deficit and domestic employment" | 12+ papers | 1995-2024 |
| "inequality and financial sector growth" | 10+ papers | 2000-2023 |

The index enables cross-series discovery that is impossible through the organization's current year-by-year browsing interface. A query about "full employment policy" retrieves results from working papers, policy notes, and public policy briefs spanning 30+ years, surfacing connections that would require days of manual browsing.

---

## Key Insight

Historical archives benefit disproportionately from semantic search. The longer the time span, the more likely it is that related work is separated by decades of intervening publications. A 125-year archive with keyword search still misses conceptual connections; a semantic index surfaces them in under a second.

---

**Corpus:** 1,621 documents | ~40,000 chunks | Streaming build with VRAM monitoring
