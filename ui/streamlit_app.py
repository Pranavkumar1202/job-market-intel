import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Job Market Intelligence", layout="wide")
st.title("Job Market Intelligence")
st.caption("Match your resume to stored job postings and see which skills the market asks for.")


def api_get(path, **params):
    response = requests.get(f"{API_URL}{path}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def api_match(uploaded_file, top):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    response = requests.post(f"{API_URL}/match", params={"top": top}, files=files, timeout=120)
    if response.status_code != 200:
        detail = response.json().get("detail", response.text) if response.content else response.text
        raise RuntimeError(f"{response.status_code}: {detail}")
    return response.json()


try:
    health = api_get("/health")
except requests.RequestException:
    st.error(
        "Cannot reach the API at " + API_URL + ". "
        "Start it in another terminal with: uvicorn src.api.main:app"
    )
    st.stop()

st.sidebar.metric("Jobs loaded", health["jobs_loaded"])

tab_match, tab_trends, tab_jobs = st.tabs(["Resume match", "Skill trends", "Browse jobs"])

with tab_match:
    uploaded = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
    top = st.slider("Number of matches", min_value=5, max_value=30, value=10)

    if st.button("Find matches", disabled=uploaded is None):
        with st.spinner("Matching..."):
            try:
                st.session_state["match"] = api_match(uploaded, top)
            except Exception as exc:
                st.session_state.pop("match", None)
                st.error(f"Matching failed: {exc}")

    result = st.session_state.get("match")
    if result:
        st.subheader("Skills found in your resume")
        st.write(", ".join(result["resume_skills"]) or "None found")

        if result["skill_gaps"]:
            st.subheader("Skills most often missing across your top matches")
            gaps = pd.DataFrame(result["skill_gaps"]).set_index("skill")
            st.bar_chart(gaps["jobs"])

        st.subheader("Best matching jobs")
        for i, job in enumerate(result["matches"], start=1):
            place = f" ({job['city']})" if job["city"] else ""
            label = f"{i}. {job['title']} - {job['company'] or 'unknown company'}{place}  |  score {job['score']:.2f}"
            with st.expander(label):
                overlap = job["skill_overlap"]
                overlap_text = f"{overlap:.0%}" if overlap is not None else "no skills detected in the ad"
                st.write(f"Similarity {job['similarity']:.2f} | Skill overlap {overlap_text}")
                st.write("You have: " + (", ".join(job["matched"]) or "-"))
                st.write("You lack: " + (", ".join(job["missing"]) or "-"))
                if job["url"]:
                    st.link_button("Open job posting", job["url"])

with tab_trends:
    limit = st.slider("Skills to show", min_value=5, max_value=30, value=15)
    trends = pd.DataFrame(api_get("/trends/skills", limit=limit))
    if trends.empty:
        st.info("No skill data yet.")
    else:
        st.bar_chart(trends.set_index("skill")["jobs"])
        st.caption("Counts come from short ad snippets, so they understate how often skills appear.")

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
