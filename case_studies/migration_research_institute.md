# Case Study: Migration Research Institute

**Domain:** International migration policy
**Corpus:** 45 documents (targeted subset from 300+ available), 563 chunks
**Challenge:** Surfacing conceptual patterns across 15 years of comparative policy research

---

## Problem

A leading migration research organization produces reports covering U.S. immigration enforcement, EU asylum policy, labor migration, and integration programs. Their website organizes publications chronologically with topic tags, but there is no way to query across documents for conceptual patterns --- for example, how "coordination failures" manifest differently in U.S. federal-local partnerships versus EU member state relationships.

Three user pain scenarios drove the query design:

1. **Journalist on deadline:** Needs to understand how asylum policy evolved across administrations, drawing from 5+ reports published over 15 years
2. **Congressional analyst:** Needs the intersection of labor market impacts and immigration enforcement, buried across separate report series
3. **Internal researcher:** Needs to verify whether a claim about enforcement accountability has antecedents in the organization's own prior work

---

## Solution

A targeted corpus of 45 key publications was indexed, producing 563 chunks. Queries were designed around user personas rather than simple keyword patterns:

| Parameter | Value |
|-----------|-------|
| Documents | 45 PDFs (curated subset) |
| Chunks | 563 |
| Chunking | 2,000 chars target, 200-char overlap |
| Embedding | intfloat/e5-large-v2, FP16, 1024-dim |
| Index | FAISS IndexFlatIP |

---

## Results

5 locked demo queries, each requiring multi-document synthesis:

| Query | Type | Min Docs Hit | Cross-Document? |
|-------|------|-------------|-----------------|
| "How has the tension between protection goals and enforcement capacity evolved from the 287(g) era through the current asylum crisis?" | Temporal | 3+ | Yes (15-year span) |
| "What coordination failures exist across both U.S. federal-local partnerships and EU member state relationships?" | Comparative | 3+ | Yes (US/EU) |
| "How does the framing of 'crisis' differ between the EU 2015-16 migration crisis and the U.S. southwest border crisis?" | Comparative | 2+ | Yes (regional) |
| "What institutional adaptations are recommended when systems designed for one era of migration face fundamentally different flows?" | Structural | 3+ | Yes (thematic) |
| "How has the accountability gap in delegated immigration enforcement programs been characterized over the past 15 years?" | Temporal | 2+ | Yes (longitudinal) |

Every query requires synthesis across multiple documents. None can be answered by a single report. The semantic index retrieves relevant chunks from 3-5 different publications per query, enabling the cross-document analysis that the organization's browse-only interface cannot support.

---

## Key Insight

The analytical depth possible with semantic search depends on query design, not just index quality. By deriving queries from user personas (journalist, analyst, researcher), the demo addresses real information needs rather than abstract capabilities. A migration researcher asking "how has accountability evolved" gets results spanning 2011-2025 from reports they may not have known existed.

Even a small corpus (45 documents) produces high-value results when queries are designed around genuine use cases.

---

**Corpus:** 45 documents | 563 chunks | Multi-document synthesis validated on 5 queries
