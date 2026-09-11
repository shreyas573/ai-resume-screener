"""
AI Resume & Job-Matching Screener
Helps recruiters shortlist candidates fast, and helps job seekers check their
own fit against a job description before applying.
"""
import streamlit as st
import pandas as pd
from utils.parser import extract_text, clean_text
from utils.anonymizer import anonymize
from utils.skills import extract_required_skills, match_skills
from utils.matcher import score_resumes, get_active_method

st.set_page_config(page_title="AI Resume & Job-Matching Screener", layout="wide")

st.title("AI Resume & Job-Matching Screener")
st.caption(
    "Semantic matching + skill-gap explainability + blind-screening bias mitigation. "
    f"Matching engine active: **{get_active_method()}**"
)

mode = st.sidebar.radio("Choose your mode", ["Recruiter (rank many resumes)", "Job Seeker (check your own fit)"])
blind_mode = st.sidebar.toggle(
    "Blind screening mode",
    value=True,
    help="Strips names, emails, phone numbers, and links before scoring, to reduce bias.",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**About blind screening:** when on, identifying details are redacted from "
    "resume text *before* it is embedded or scored, so ranking is driven by "
    "skills and experience rather than identity signals."
)


def read_uploaded_files(uploaded_files):
    parsed = []
    for f in uploaded_files:
        raw = extract_text(f.read(), f.name)
        parsed.append({"filename": f.name, "raw_text": clean_text(raw)})
    return parsed


# ---------------------------------------------------------------------------
# RECRUITER MODE
# ---------------------------------------------------------------------------
if mode.startswith("Recruiter"):
    st.subheader("Recruiter mode: rank a batch of resumes against one job description")

    col1, col2 = st.columns(2)
    with col1:
        jd_file = st.file_uploader("Upload job description (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])
        jd_text_input = st.text_area("...or paste job description text", height=150)
    with col2:
        resume_files = st.file_uploader(
            "Upload candidate resumes (.pdf, .docx, .txt) - multiple allowed",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
        )

    if st.button("Run screening", type="primary"):
        jd_text = ""
        if jd_file is not None:
            jd_text = clean_text(extract_text(jd_file.read(), jd_file.name))
        elif jd_text_input.strip():
            jd_text = clean_text(jd_text_input)

        if not jd_text:
            st.error("Please provide a job description (upload or paste).")
        elif not resume_files:
            st.error("Please upload at least one resume.")
        else:
            with st.spinner("Scoring candidates..."):
                resumes = read_uploaded_files(resume_files)
                required_skills = extract_required_skills(jd_text)

                score_inputs = []
                for r in resumes:
                    text_for_scoring = anonymize(r["raw_text"]) if blind_mode else r["raw_text"]
                    score_inputs.append(text_for_scoring)

                scores = score_resumes(jd_text, score_inputs)

                rows = []
                for r, score in zip(resumes, scores):
                    skill_result = match_skills(r["raw_text"], required_skills)
                    rows.append({
                        "Candidate File": r["filename"],
                        "Match Score": round(score * 100, 1),
                        "Skills Matched": f"{len(skill_result['matched'])}/{len(required_skills)}" if required_skills else "N/A",
                        "Missing Skills": ", ".join(skill_result["missing"]) if skill_result["missing"] else "None",
                    })

                df = pd.DataFrame(rows).sort_values("Match Score", ascending=False).reset_index(drop=True)
                df.index = df.index + 1

            st.success(f"Screened {len(resumes)} resumes against {len(required_skills)} required skills detected in the JD.")
            if required_skills:
                st.write("**Required skills detected in JD:** " + ", ".join(required_skills))
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "Download results as CSV",
                df.to_csv(index=False).encode("utf-8"),
                "screening_results.csv",
                "text/csv",
            )

# ---------------------------------------------------------------------------
# JOB SEEKER MODE
# ---------------------------------------------------------------------------
else:
    st.subheader("Job Seeker mode: check how well your resume fits a job description")

    col1, col2 = st.columns(2)
    with col1:
        resume_file = st.file_uploader("Upload your resume (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
    with col2:
        jd_file = st.file_uploader("Upload the job description (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"], key="jd_seeker")
        jd_text_input = st.text_area("...or paste job description text", height=150, key="jd_text_seeker")

    if st.button("Check my fit", type="primary"):
        jd_text = ""
        if jd_file is not None:
            jd_text = clean_text(extract_text(jd_file.read(), jd_file.name))
        elif jd_text_input.strip():
            jd_text = clean_text(jd_text_input)

        if not resume_file or not jd_text:
            st.error("Please upload your resume and provide a job description.")
        else:
            with st.spinner("Analyzing fit..."):
                resume_text = clean_text(extract_text(resume_file.read(), resume_file.name))
                required_skills = extract_required_skills(jd_text)
                skill_result = match_skills(resume_text, required_skills)
                score = score_resumes(jd_text, [resume_text])[0]

            st.metric("Overall Match Score", f"{round(score * 100, 1)}%")
            if required_skills:
                st.write(f"**Skills matched:** {len(skill_result['matched'])}/{len(required_skills)}")
                st.write("✅ " + ", ".join(skill_result["matched"]) if skill_result["matched"] else "No listed skills matched.")
                if skill_result["missing"]:
                    st.write("⚠️ **Consider adding or highlighting:** " + ", ".join(skill_result["missing"]))
                else:
                    st.write("You cover every detected required skill.")
            else:
                st.info("No skills from the built-in dictionary were detected in this job description.")
