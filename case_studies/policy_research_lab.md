# Case Study: Policy Research Lab

**Domain:** Multi-sector policy research (criminal justice, homelessness, education, labor, health)
**Corpus:** 102 documents, 2,760 chunks
**Challenge:** Cross-topic discovery across siloed research areas

---

## Problem

A university-affiliated policy research lab produces studies across six distinct policy areas: criminal justice, homelessness, education, labor markets, safety net programs, and health. Their publications page organizes work by topic, which means a researcher looking at homelessness prevention will never see related work on housing vouchers filed under "safety net," or workforce reentry studies filed under "criminal justice."

The lab's own website has no full-text search. Visitors browse by topic category or scroll a chronological list. Cross-topic insights --- the lab's most distinctive output --- are invisible to their own audience.

---

## Solution

All 102 publications were indexed with the standard pipeline:

| Parameter | Value |
|-----------|-------|
| Documents | 102 PDFs |
| Chunks | 2,760 |
| Chunking | ~800 tokens target, 100-token overlap |
| Embedding | intfloat/e5-large-v2, FP16, 1024-dim |
| Index | FAISS IndexFlatIP |

---

## Results

10 queries were tested across the corpus. Mean top-1 cosine similarity: **0.87**.

| Query | Top Score | Cross-Topic? |
|-------|-----------|-------------|
| "What programs help prevent homelessness?" | 0.863 | Yes (housing + safety net) |
| "How does food assistance eligibility work for college students?" | 0.891 | Yes (education + safety net) |
| "What is the impact of minimum wage increases?" | 0.874 | Yes (labor + economy) |
| "What does research show about criminal record clearance?" | 0.858 | Yes (criminal justice + labor) |
| "How effective are job training programs?" | 0.857 | Yes (labor + education) |
| "What happened after sentencing reform?" | 0.892 | No (criminal justice) |
| "How did unemployment insurance respond to the pandemic?" | 0.853 | Yes (labor + safety net) |
| "What interventions help transition-aged youth?" | 0.851 | Yes (education + safety net) |
| "What do studies show about racial disparities in policing?" | 0.871 | No (criminal justice) |
| "What affects tax credit take-up rates?" | 0.868 | Yes (safety net + labor) |

The strongest results came from queries that span topic boundaries. "Food assistance for college students" (score: 0.891) connects education research with safety net program evaluations --- a search that returns nothing on the organization's topic-filtered browse page.

---

## Key Insight

Organizations that produce cross-cutting policy research are paradoxically worst served by their own topic-based navigation. The more interdisciplinary the work, the more a semantic index improves discovery. This lab's most valuable output --- studies connecting criminal justice to labor markets, or education to safety net access --- is exactly what their current interface hides.

---

**Corpus:** 102 documents | 2,760 chunks | Average relevance: 0.87
