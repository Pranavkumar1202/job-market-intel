import hashlib
import html
import re

from src.ingestion.parsing import extract_fields

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def clean_text(text):
    """Strip HTML tags and entities, collapse whitespace."""
    if not text:
        return None
    text = html.unescape(TAG_RE.sub(" ", text))
    text = WS_RE.sub(" ", text).strip()
    return text or None


def normalize_title(title):
    if not title:
        return None
    return WS_RE.sub(" ", title).strip().lower() or None


def extract_city(location):
    """'Bhubaneswar, Khordha' -> 'Bhubaneswar'; 'India' -> None."""
    if not location:
        return None
    first = location.split(",")[0].strip()
    return None if first.lower() == "india" or not first else first


def make_dedup_key(company, title_normalized, location, external_id):
    """Same company + title + location = same job.
    If company is unknown, fall back to the external id so unrelated
    jobs are not merged by mistake."""
    if company:
        basis = "|".join([
            company.strip().lower(),
            title_normalized or "",
            (location or "").strip().lower(),
        ])
    else:
        basis = f"id|{external_id}"
    return hashlib.md5(basis.encode("utf-8")).hexdigest()


def clean_job(payload: dict) -> dict:
    base = extract_fields(payload)
    title_norm = normalize_title(base["title"])
    return {
        "external_id": base["external_id"],
        "title": clean_text(base["title"]),
        "title_normalized": title_norm,
        "company": clean_text(base["company"]),
        "location": clean_text(base["location"]),
        "city": extract_city(clean_text(base["location"])),
        "category": (payload.get("category") or {}).get("label"),
        "contract_type": payload.get("contract_type"),
        "contract_time": payload.get("contract_time"),
        "salary_min": base["salary_min"],
        "salary_max": base["salary_max"],
        "description": clean_text(base["description"]),
        "url": base["url"],
        "posted_at": base["created"],
        "dedup_key": make_dedup_key(
            clean_text(base["company"]), title_norm,
            clean_text(base["location"]), base["external_id"],
        ),
    }