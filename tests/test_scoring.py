from src.matching.scoring import rank_jobs, skill_gaps


def make_jobs():
    return [
        {"id": 1, "embedding": [1.0, 0.0, 0.0], "skills": {"Python", "SQL"}},
        {"id": 2, "embedding": [0.0, 1.0, 0.0], "skills": {"Airflow", "dbt"}},
        {"id": 3, "embedding": [0.0, 0.0, 1.0], "skills": set()},
    ]


def test_most_similar_job_ranks_first():
    results = rank_jobs([1.0, 0.0, 0.0], {"Python", "SQL"}, make_jobs())
    assert results[0]["id"] == 1


def test_matched_and_missing_skills():
    results = rank_jobs([1.0, 0.0, 0.0], {"Python"}, make_jobs())
    top = results[0]
    assert top["matched"] == ["Python"]
    assert top["missing"] == ["SQL"]
    assert top["skill_overlap"] == 0.5


def test_job_without_skills_is_flagged():
    results = rank_jobs([0.0, 0.0, 1.0], {"Python"}, make_jobs())
    top = results[0]
    assert top["id"] == 3
    assert top["skill_overlap"] is None


def test_top_n_and_embedding_not_returned():
    results = rank_jobs([1.0, 0.0, 0.0], set(), make_jobs(), top_n=2)
    assert len(results) == 2
    assert "embedding" not in results[0]


def test_empty_jobs_returns_empty_list():
    assert rank_jobs([1.0, 0.0, 0.0], {"Python"}, []) == []


def test_job_with_many_skills_beats_job_with_one_when_similarity_is_equal():
    jobs = [
        {"id": 1, "embedding": [1.0, 0.0], "skills": {"Python"}},
        {"id": 2, "embedding": [1.0, 0.0], "skills": {"Python", "SQL", "Pandas"}},
    ]
    results = rank_jobs([1.0, 0.0], {"Python", "SQL", "Pandas"}, jobs)
    assert results[0]["id"] == 2


def test_skill_gaps_counts_missing_skills():
    results = rank_jobs([1.0, 0.0, 0.0], {"Python"}, make_jobs(), top_n=3)
    gaps = dict(skill_gaps(results))
    assert gaps["SQL"] == 1
    assert gaps["Airflow"] == 1
