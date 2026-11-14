# Job Market Intelligence Platform

Pipeline that ingests job postings, extracts skills and matches resumes to jobs.

## Setup
1. Create a virtual environment and run `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your Adzuna keys and database URL
3. Install PostgreSQL, then create a database: `psql -U postgres -c "CREATE DATABASE jobs;"`
4. Create the table: `psql -U postgres -d jobs -f sql/001_create_raw_jobs.sql`
5. Run ingestion: `python -m src.ingestion.fetch_jobs`
6. Run tests: `pytest`

## Status
- [x] Raw ingestion into PostgreSQL
- [ ] Cleaning and deduplication
- [ ] Skill extraction
- [ ] Matching, API and dashboard