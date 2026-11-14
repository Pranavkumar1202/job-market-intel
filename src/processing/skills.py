import re

# name -> (category, aliases). Aliases are matched case-insensitively.
# Ambiguous short names are deliberately avoided (e.g. plain "R", "Go", "C").
SKILLS = {
    "Python": ("language", ["python"]),
    "SQL": ("language", ["sql", "t-sql", "pl/sql"]),
    "R": ("language", ["r programming", "rstudio"]),
    "Java": ("language", ["java"]),
    "JavaScript": ("language", ["javascript"]),
    "PostgreSQL": ("database", ["postgresql", "postgres"]),
    "MySQL": ("database", ["mysql"]),
    "Snowflake": ("database", ["snowflake"]),
    "Excel": ("tool", ["excel"]),
    "Power BI": ("bi", ["power bi", "powerbi"]),
    "Tableau": ("bi", ["tableau"]),
    "Looker": ("bi", ["looker"]),
    "ETL": ("data engineering", ["etl", "elt"]),
    "Airflow": ("data engineering", ["airflow"]),
    "dbt": ("data engineering", ["dbt"]),
    "Spark": ("data engineering", ["spark", "pyspark"]),
    "Hadoop": ("data engineering", ["hadoop"]),
    "Kafka": ("data engineering", ["kafka"]),
    "AWS": ("cloud", ["aws", "amazon web services"]),
    "Azure": ("cloud", ["azure"]),
    "GCP": ("cloud", ["gcp", "google cloud"]),
    "Docker": ("devops", ["docker"]),
    "Git": ("devops", ["git", "github"]),
    "Pandas": ("library", ["pandas"]),
    "NumPy": ("library", ["numpy"]),
    "scikit-learn": ("ml", ["scikit-learn", "sklearn"]),
    "TensorFlow": ("ml", ["tensorflow"]),
    "PyTorch": ("ml", ["pytorch"]),
    "Machine Learning": ("ml", ["machine learning"]),
    "NLP": ("ml", ["nlp", "natural language processing"]),
    "Generative AI": ("ml", ["generative ai", "genai", "llm", "llms", "large language model"]),
    "Statistics": ("analytics", ["statistics", "statistical"]),
    "Data Visualization": ("analytics", ["data visualization", "data visualisation"]),
    "FastAPI": ("backend", ["fastapi"]),
    "Flask": ("backend", ["flask"]),
}

_BOUNDARY_BEFORE = r"(?<![a-z0-9+#])"
_BOUNDARY_AFTER = r"(?![a-z0-9+#])"

_PATTERNS = [
    (
        name,
        re.compile(
            _BOUNDARY_BEFORE
            + "(?:" + "|".join(re.escape(a) for a in aliases) + ")"
            + _BOUNDARY_AFTER
        ),
    )
    for name, (_, aliases) in SKILLS.items()
]


def skill_catalog():
    return [(name, category) for name, (category, _) in SKILLS.items()]


def extract_skills(*texts):
    """Return the set of skill names found in the given texts."""
    text = " ".join(t for t in texts if t).lower()
    return {name for name, rx in _PATTERNS if rx.search(text)}
