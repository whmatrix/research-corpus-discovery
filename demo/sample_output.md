# Sample Output

Example terminal output from `query.py` running against a regional economics corpus (8,339 chunks, 178 documents).

---

## Single Query

```
$ python scripts/query.py \
    --index ./index/faiss.index \
    --chunks ./index/chunks.jsonl \
    --query "What public-private partnership models have been evaluated?"

Loading index ...
Loading model on cuda ...

Query: What public-private partnership models have been evaluated?
Results: 5

============================================================
[1]  Score: 0.8610
  Document : economic_resilience_2015
  Title    : Economic Resilience
  Year     : 2015
  Section  : Infrastructure Partnerships

  the private partner and performance contracts that preclude
  change orders. This model ensures that the private sector partner
  is accountable for maintenance over the life of the contract ...

============================================================
[2]  Score: 0.8400
  Document : investing_infrastructure_2006
  Title    : Investing in California's Infrastructure
  Year     : 2006
  Section  : Partnership Models

  Three types of public and private sector partnerships.
  Type 1: Design-Build. Type 2: Design-Build-Operate-Maintain.
  Type 3: Design-Build-Finance-Operate ...

============================================================
[3]  Score: 0.8400
  Document : partnerships_california_2018
  Title    : Partnerships in California
  Year     : 2018
  Section  : Policy Framework

  environmental Protection Act approval. Combined with state
  infrastructure plan would extend the term of the contract.
  The public sector must balance transparency with ...

============================================================
[4]  Score: 0.8390
  Document : partnerships_california_2018
  Title    : Partnerships in California
  Year     : 2018
  Section  : Introduction

  by a public policy organization that includes hundreds of
  the region's largest employers and is committed to keeping
  the region competitive and economically vibrant ...

============================================================
[5]  Score: 0.8370
  Document : framework_conditions_2010
  Title    : Framework Conditions
  Year     : 2010
  Section  : Investment Models

  administration and management. In this context, the following
  threshold issues must be addressed: The public sector must
  determine the scope of the partnership ...
```

---

## JSON Output

```
$ python scripts/query.py \
    --index ./index/faiss.index \
    --chunks ./index/chunks.jsonl \
    --query "minimum wage effects on employment" \
    --json -k 3

[
  {
    "rank": 1,
    "score": 0.88,
    "doc_id": "wp_0233",
    "title": "Effects of the Minimum Wage on Employment Dynamics",
    "year": 2015,
    "section": "Results",
    "snippet": "The estimated employment effects are concentrated among ..."
  },
  {
    "rank": 2,
    "score": 0.87,
    "doc_id": "wp_0298",
    "title": "Payroll, Revenue, and Labor Demand Effects of the Minimum Wage",
    "year": 2019,
    "section": "Empirical Strategy",
    "snippet": "We estimate the effect of minimum wage increases on ..."
  },
  {
    "rank": 3,
    "score": 0.86,
    "doc_id": "wp_0161",
    "title": "Employment and Training Policy in the United States",
    "year": 2009,
    "section": "Policy Analysis",
    "snippet": "The interaction between minimum wage policy and training ..."
  }
]
```

---

## Interactive Mode

```
$ python scripts/query.py \
    --index ./index/faiss.index \
    --chunks ./index/chunks.jsonl

Semantic Search  (8339 chunks indexed)
Enter queries below. Ctrl+C to exit.

Query: how has unemployment research evolved
[results displayed]

Query: displaced workers reemployment outcomes
[results displayed]

Query: ^C
Exiting.
```
