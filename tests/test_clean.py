from src.processing.clean import (
    clean_text, extract_city, make_dedup_key, normalize_title,
)


def test_clean_text_strips_html_and_entities():
    assert clean_text("<p>Python &amp; SQL</p>  skills") == "Python & SQL skills"


def test_clean_text_handles_none_and_empty():
    assert clean_text(None) is None
    assert clean_text("   ") is None


def test_normalize_title():
    assert normalize_title("  Data   Analyst ") == "data analyst"


def test_extract_city():
    assert extract_city("Bhubaneswar, Khordha") == "Bhubaneswar"
    assert extract_city("India") is None
    assert extract_city(None) is None


def test_same_job_gets_same_key():
    a = make_dedup_key("H&M", "data analyst", "India", "1")
    b = make_dedup_key("h&m ", "data analyst", "india", "2")
    assert a == b


def test_unknown_company_does_not_merge_different_jobs():
    a = make_dedup_key(None, "data analyst", "India", "1")
    b = make_dedup_key(None, "data analyst", "India", "2")
    assert a != b