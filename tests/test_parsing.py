import json
from pathlib import Path

from src.ingestion.parsing import extract_fields, get_external_id

FIXTURE = Path(__file__).parent / "fixtures" / "sample_job.json"


def load_job():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_extract_fields_returns_expected_keys():
    fields = extract_fields(load_job())
    assert set(fields) == {
        "external_id", "title", "company", "location",
        "salary_min", "salary_max", "description", "url", "created",
    }
    assert fields["title"]


def test_missing_salary_becomes_none():
    job = load_job()
    job.pop("salary_min", None)
    job.pop("salary_max", None)
    fields = extract_fields(job)
    assert fields["salary_min"] is None
    assert fields["salary_max"] is None


def test_missing_company_does_not_crash():
    job = load_job()
    job.pop("company", None)
    assert extract_fields(job)["company"] is None


def test_external_id_is_string():
    assert isinstance(get_external_id(load_job()), str)