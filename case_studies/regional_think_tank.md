# Case Study: Regional Think Tank

**Domain:** Regional economic policy (trade, innovation, housing, infrastructure, climate)
**Corpus:** 178 documents, 8,339 chunks
**Challenge:** Cross-temporal, multi-topic synthesis for a small research team

---

## Problem

A regional think tank with a team of 5-6 staff has produced research for 25 years across trade, innovation, housing, infrastructure, healthcare, climate, and workforce development. The publication archive contains 180 reports spanning 2000-2025, but the organization's website offers only a flat chronological list.

The core friction: a researcher preparing a report on regional infrastructure investment cannot efficiently locate prior work on public-private partnerships, climate resilience bonds, or workforce gaps that are directly relevant but filed under different topic headings and published years apart.

---

## Solution

178 PDFs were indexed (2 scanned-image documents were deferred). The build completed in under a minute:

| Parameter | Value |
|-----------|-------|
| Documents | 178 PDFs (771 MB) |
| Chunks | 8,339 |
| Chunking | 1,000 tokens target, 150-token overlap |
| Embedding | intfloat/e5-large-v2, FP16, 1024-dim |
| Index | FAISS IndexFlatIP, 34 MB |
| Build time | ~43 seconds embedding, ~194 chunks/sec |
| VRAM | < 3 GB |

---

## Results

8 queries tested across the corpus:

| Query | Top Score | Time Span Retrieved |
|-------|-----------|-------------------|
| "How has regional trade exposure evolved, and which sectors show the highest volatility?" | 0.844 | 2000-2010 |
| "What recurring constraints appear across housing and infrastructure reports?" | 0.809 | 2009-2016 |
| "Which reports link innovation investment to regional inequality outcomes?" | 0.824 | 2008-2012 |
| "How do climate-related economic risks surface across otherwise unrelated reports?" | 0.827 | 2020 |
| "What public-private partnership models have been evaluated for infrastructure projects?" | 0.861 | 2006-2018 |
| "How has the region's relationship with international trade partners evolved?" | 0.857 | 2006-2014 |
| "What workforce development strategies address the region's skills gaps?" | 0.849 | 2015-2017 |
| "What economic impacts have been documented from wildfires and natural disasters?" | 0.835 | 2020-2021 |

The public-private partnership query (score: 0.861) retrieves results from 4 different reports spanning 12 years (2006-2018), including an infrastructure investment report, a resilience assessment, a partnership evaluation, and a framework conditions analysis. This cross-document retrieval takes < 100ms versus the hours of manual browsing needed to locate these connections.

---

## Key Insight

Small research teams benefit most from semantic search over their own archives. With 5-6 staff producing reports for 25 years, institutional memory is distributed across documents that predate most current team members. The index acts as organizational memory --- a researcher joining today can query 25 years of prior work as easily as someone who has been there from the start.

The 34 MB index replaces 771 MB of PDFs as the primary discovery interface while preserving full document access for deep reading.

---

**Corpus:** 178 documents | 8,339 chunks | Average top score: 0.838 | Build time: < 1 minute
