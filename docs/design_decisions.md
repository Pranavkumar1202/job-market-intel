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

## Skill extraction evaluation, batch 2 (extractor-assisted review)
- 30 jobs reviewed by hand with the extractor's findings visible; each confirmed or corrected.
- Rule: a skill counts only if the visible text asks for it or says the role uses it. Skills mentioned only in the company description do not count.
- Data limit: the Adzuna API returns descriptions capped at about 500 characters (raw_jobs: max 500, average 494, 144 of 150 postings at or near the cap). Both the labels and the extractor see only the start of each ad, often the company intro, so results describe extraction on that snippet.
- Corrections: 3 Python labels (jobs 116, 118, 122) removed because the skill was not in the visible text.
- Result: precision [81.8]%, recall [95.7]%, F1 [88.2]% (TP [45], FP [10], FN [2]).
- Caveat: the extractor's output was visible while reviewing, so precision is reliable but recall is likely overstated. Only 30 jobs.
- Main error types: [skills mentioned only in company descriptions; ...].
- Batch 1 (23 jobs, about 94%) has the same snippet limit and review bias.

## Skill extraction evaluation, batch 2 (extractor-assisted review)
- 30 jobs reviewed by hand with the extractor's findings visible; each confirmed or corrected.
- Rule: a skill counts only if the visible text asks for it or says the role uses it. Skills mentioned only in the company description do not count.
- Data limit: the Adzuna API returns descriptions capped at about 500 characters (raw_jobs: max 500, average 494, 144 of 150 postings at or near the cap). Labels and extractor both see only the start of each ad, often the company intro, so results describe extraction on that snippet.
- Corrections: 3 Python labels (jobs 116, 118, 122) removed because the skill was not in the visible text.
- Result: precision 81.8%, recall 95.7%, F1 88.2% (TP 45, FP 10, FN 2).
- False positives (10): Generative AI 3, Machine Learning 2, NLP 2, Python 2, PyTorch 1. I have not yet checked each case, so some may be skills I did not label rather than extractor errors.
- False negatives (2): Generative AI 1, NLP 1.
- Caveat: the extractor's output was visible while reviewing, so precision is reliable but recall is likely overstated. Only 30 jobs.
- Batch 1 (23 jobs, about 94%) has the same snippet limit and review bias.