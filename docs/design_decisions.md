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