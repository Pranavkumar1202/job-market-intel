# Design decisions

## Data source
Adzuna API (free test tier, 25 calls). Chosen because it has documented terms and an India endpoint.

## Findings from the first sample (10 jobs)
- Salary missing in 10/10 jobs -> salary is an optional field.
- Company missing in 1/10 -> cleaning must handle nulls.
- Description is a ~470-character snippet, not full text -> skill extraction recall will be limited; I will measure and report it.
- Useful fields: category, contract_type, contract_time, created, redirect_url.

## Constraints
- Limited API calls: develop against saved JSON, and fetch in batches (up to 50 results per call).

## Skill extraction evaluation
- 23 jobs hand-labelled from the first 30 exported; labels use the same skill dictionary as the extractor.
- Result: precision 93.75%, recall 93.75%, F1 93.75% (15 TP, 1 FP, 1 FN).
- Caveat: the first labelling pass was careless (many "no skills" labels), and I corrected labels after seeing the extractor's matches. That makes these numbers optimistic. A cleaner test would label a fresh batch of jobs before running the extractor.
- Known errors:
  - False positive: "Generative AI" taken from a company description, not a job requirement.
  - False negative: "R" is not matched, because a single letter is too ambiguous to match safely.
- Recall is also limited by the ~470-character description snippets.
- Observed: the same ad (e.g. Amicus Therapeutics, Data Analyst) appears several times with different locations, so the location-based dedup key misses it.