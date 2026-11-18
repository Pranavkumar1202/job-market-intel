import os
from html import escape

import pandas as pd
import requests
import streamlit as st

from components import bar_row_html, chips_html, score_label

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Job Market Intelligence", page_icon=None, layout="wide")

st.markdown(
    """
<style>
.block-container {padding-top: 2rem; max-width: 1150px;}
.hero {background: linear-gradient(135deg, #0F766E 0%, #115E59 60%, #134E4A 100%);
       padding: 1.6rem 1.9rem; border-radius: 16px; color: #fff; margin-bottom: 1.2rem;}
.hero h1 {margin: 0; font-size: 1.9rem; color: #fff; padding: 0;}
.hero p {margin: .35rem 0 0; opacity: .92; font-size: 1rem;}
.chip {display: inline-block; padding: 2px 11px; margin: 2px 5px 2px 0; border-radius: 999px;
       font-size: .78rem; font-weight: 600;}
.chip-ok {background: #DCFCE7; color: #166534;}
.chip-miss {background: #FEE2E2; color: #991B1B;}
.chip-skill {background: #E0F2FE; color: #075985;}
.chip-none {background: #F1F5F9; color: #64748B;}
.score-pill {float: right; background: #0F766E; color: #fff; padding: 4px 13px;
             border-radius: 999px; font-weight: 700; font-size: .9rem;}
.job-title {font-size: 1.08rem; font-weight: 700; color: #0F172A;}
.job-meta {color: #64748B; font-size: .88rem; margin: 2px 0 6px;}
.bar-row {display: flex; align-items: center; gap: 12px; margin: 7px 0;}
.bar-label {width: 150px; font-size: .88rem; color: #0F172A;}
.bar-track {flex: 1; background: #E2E8F0; border-radius: 999px; height: 11px;}
.bar-fill {background: linear-gradient(90deg, #14B8A6, #0F766E); height: 11px; border-radius: 999px;}
.bar-value {width: 36px; text-align: right; font-size: .85rem; color: #475569;}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><h1>Job Market Intelligence</h1>'
    "<p>Upload your resume, see the best-matching jobs, and learn which skills the market asks for.</p></div>",
    unsafe_allow_html=True,
)


def api_get(path, **params):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def api_match(uploaded_file, top):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    response = requests.post(f"{API_URL}/match", params={"top": top}, files=files, timeout=120)
    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(f"{response.status_code}: {detail}")
    return response.json()


try:
    health = api_get("/health")
except requests.RequestException:
    st.error(
        "Cannot reach the API at " + API_URL + ". "
        "Start it in another terminal with: uvicorn src.api.main:app, then refresh this page."
    )
    st.stop()

with st.sidebar:
    st.header("About")
    st.metric("Jobs in the database", health["jobs_loaded"])
    st.markdown(
        "**How matching works**\n\n"
        "Your resume and every job are turned into embeddings. The score combines "
        "meaning similarity (70%) with the share of the job's listed skills you already have (30%), "
        "weighted by how many skills the ad lists."
    )
    top = st.slider("Jobs to show", min_value=5, max_value=30, value=10)
    st.caption("Job text comes from short ad snippets, so skill counts are understated.")


def job_card(rank, job):
    place = f" | {escape(job['city'])}" if job["city"] else ""
    company = escape(job["company"] or "Unknown company")
    overlap = job["skill_overlap"]
    overlap_text = f"{overlap:.0%} of listed skills" if overlap is not None else "no skills detected in the ad"
    with st.container(border=True):
        st.markdown(
            f'<span class="score-pill">{score_label(job["score"])} / 100</span>'
            f'<div class="job-title">{rank}. {escape(job["title"] or "Untitled")}</div>'
            f'<div class="job-meta">{company}{place}</div>',
            unsafe_allow_html=True,
        )
        st.progress(min(max(float(job["score"]), 0.0), 1.0))
        st.markdown(
            f'<div class="job-meta">Similarity {job["similarity"]:.2f} | Skill overlap: {escape(overlap_text)}</div>',
            unsafe_allow_html=True,
        )
        left, right = st.columns(2)
        left.markdown("**You have**")
        left.markdown(chips_html(job["matched"], "ok"), unsafe_allow_html=True)
        right.markdown("**You lack**")
        right.markdown(chips_html(job["missing"], "miss", empty="nothing missing in this ad"), unsafe_allow_html=True)
        if job["url"]:
            st.link_button("View posting", job["url"])


tab_match, tab_trends, tab_jobs = st.tabs(["Match my resume", "Market trends", "Browse jobs"])

with tab_match:
    uploaded = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
    if st.button("Find my best matches", type="primary", disabled=uploaded is None):
        with st.spinner("Reading your resume and ranking jobs..."):
            try:
                st.session_state["match"] = api_match(uploaded, 50)
            except Exception as exc:
                st.session_state.pop("match", None)
                st.error(f"Matching failed: {exc}")

    result = st.session_state.get("match")
    if not result:
        st.info("Upload a resume and click the button to see your matches.")
    else:
        best = result["matches"][0]["score"] if result["matches"] else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Skills found in your resume", len(result["resume_skills"]))
        c2.metric("Best match score", f"{score_label(best)} / 100")
        c3.metric("Jobs compared", health["jobs_loaded"])

        st.subheader("Your skills")
        st.markdown(chips_html(result["resume_skills"], "skill"), unsafe_allow_html=True)

        if result["skill_gaps"]:
            st.subheader("Skills to learn next")
            st.caption("Skills most often missing from your resume across your top 30 matches.")
            peak = max(g["jobs"] for g in result["skill_gaps"])
            st.markdown(
                "".join(bar_row_html(g["skill"], g["jobs"], peak) for g in result["skill_gaps"]),
                unsafe_allow_html=True,
            )

        st.subheader("Matching jobs")
        view = st.radio("Show", ["Best matches", "Jobs where I lack skills"], horizontal=True)
        matches = result["matches"]
        if view == "Jobs where I lack skills":
            matches = [m for m in matches if m["missing"]]
            st.caption(
                "Jobs from your top 50 matches whose ads list at least one skill missing "
                "from your resume. These show what to learn."
            )
        shown = matches[:top]
        if not shown:
            st.info("No jobs found for this view.")
        for i, job in enumerate(shown, start=1):
            job_card(i, job)

with tab_trends:
    limit = st.slider("Skills to show", min_value=5, max_value=30, value=15)
    trends = api_get("/trends/skills", limit=limit)
    if not trends:
        st.info("No skill data yet.")
    else:
        st.subheader("Most requested skills")
        peak = max(t["jobs"] for t in trends)
        st.markdown(
            "".join(bar_row_html(t["skill"], t["jobs"], peak) for t in trends),
            unsafe_allow_html=True,
        )
        st.caption("Number of job ads that mention each skill. Ads are short snippets, so counts are understated.")

with tab_jobs:
    query = st.text_input("Search job titles", "")
    count = st.slider("Rows", min_value=5, max_value=100, value=20)
    jobs = api_get("/jobs", q=query or None, limit=count)
    if jobs:
        frame = pd.DataFrame(jobs)[["title", "company", "city", "category", "url"]]
        st.dataframe(
            frame,
            column_config={"url": st.column_config.LinkColumn("Link")},
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No jobs match that search.")
