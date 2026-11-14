from src.processing.skills import extract_skills


def test_finds_basic_skills():
    assert {"Python", "SQL"} <= extract_skills("Need Python and SQL experience")


def test_sql_not_matched_inside_mysql():
    found = extract_skills("Experience with MySQL")
    assert "MySQL" in found
    assert "SQL" not in found


def test_java_not_matched_inside_javascript():
    found = extract_skills("Strong JavaScript skills")
    assert "JavaScript" in found
    assert "Java" not in found


def test_multi_word_and_case_insensitive():
    assert "Power BI" in extract_skills("Build dashboards in POWER BI")


def test_empty_and_none_inputs():
    assert extract_skills(None, "") == set()
