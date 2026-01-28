# Case Studies: Semantic Search Across Research Corpora

This tool was tested on **10 policy and economics research organizations** spanning different sizes, geographies, topic domains, and archive depths. Four representative case studies are detailed below.

All documents indexed were publicly available research publications downloaded from each organization's website. No private or internal materials were used.

---

## Summary

| Case Study | Corpus Size | Chunks | Time Span | Domain |
|------------|------------|--------|-----------|--------|
| [Legacy Economics Archive](legacy_economics_archive.md) | 1,621 docs | ~40,000 | 1900-2025 | Economics |
| [Policy Research Lab](policy_research_lab.md) | 102 docs | 2,760 | 2015-2025 | Multi-sector policy |
| [Migration Research Institute](migration_research_institute.md) | 45 docs | 563 | 2001-2025 | Migration policy |
| [Regional Think Tank](regional_think_tank.md) | 178 docs | 8,339 | 2000-2025 | Regional economics |

**Additional orgs tested (not detailed):** An Australian public policy institute (284 docs), a foreign policy research center (142 docs), a water policy institute (691 docs), a labor economics archive (413 docs), a progressive policy institute (629 docs), and a state-level economic research center (251 docs).

---

## What These Case Studies Demonstrate

1. **Scale flexibility** - From 45 documents to 1,621, the same pipeline produces usable indexes
2. **Domain agnosticism** - Economics, migration, water policy, foreign policy, labor markets
3. **Temporal depth** - Modern archives (10 years) and historical archives (125 years)
4. **Cross-document discovery** - Queries that surface connections no keyword search can find
5. **Consistent retrieval quality** - Mean top-1 cosine similarity of 0.82-0.89 across all corpora
