# AI Resume & Job-Matching Screener

A bias-audited, explainable resume screening tool that serves **two audiences**:
- **Recruiters** — upload a job description + a batch of resumes, get a ranked
  shortlist with match scores and skill-gap breakdowns.
- **Job seekers** — upload your own resume + a job description, get an instant
  fit score and see exactly which required skills you're missing.

## Why this project

Manual resume screening is slow and keyword-based ATS filters miss qualified
candidates who phrase things differently than the job posting. This tool uses
semantic matching (not just keyword search) plus a **blind-screening mode**
that strips names, emails, phone numbers, and links before scoring — reducing
the influence of identity signals on the match score.

## Features

- **Semantic matching** — Sentence-Transformers embeddings (`all-MiniLM-L6-v2`)
  score meaning-level similarity between a JD and a resume, not just shared
  keywords. Falls back automatically to TF-IDF + cosine similarity if the
  embedding model can't be loaded (e.g. no internet access), so the app
  never breaks.
- **Blind-screening mode** — identifying details are redacted from resume
  text *before* it's embedded or scored (toggle in the sidebar).
- **Skill-gap explainability** — for every resume, shows which required
  skills (parsed from the JD against a built-in skill dictionary) are present
  and which are missing — not just an opaque score.
- **Dual mode** — recruiter batch-ranking view and a job-seeker self-check view,
  from the same underlying pipeline.
- **CSV export** of recruiter results.

## Architecture

```
app.py                 Streamlit UI (recruiter + job-seeker modes)
utils/parser.py         PDF/DOCX/TXT text extraction
utils/anonymizer.py      Blind-screening PII redaction
utils/skills.py          Skill dictionary + skill-gap extraction
utils/matcher.py         Embedding (Sentence-Transformers) or TF-IDF scoring
utils/evaluation.py      Precision@k against a hand-labeled eval set
sample_data/             Sample JD + resumes for demo/testing
```

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Try it immediately with the files in `sample_data/`: upload
`jd_data_analyst.txt` as the job description and both `resume_candidate_A.txt`
and `resume_candidate_B.txt` as resumes in Recruiter mode.

## Evaluation methodology

Match scores are inherently subjective (there's no universal "correct"
ranking), so this project is evaluated the honest way: a hand-labeled set of
30-50 resume/JD pairs (fit / not fit / maybe), scored with **precision@5** —
see `utils/evaluation.py`. Quote this number, not the raw similarity score,
when describing project results.

## Known limitations (v1)

- Parsing assumes reasonably well-structured PDF/DOCX resumes; heavily
  graphic or multi-column formats may parse imperfectly.
- The skill dictionary is a fixed list (easy to extend in `utils/skills.py`)
  rather than open-domain skill extraction.
- Blind-screening mode reduces but does not eliminate indirect bias signals
  (e.g. writing style, activity names) — treat it as a mitigation, not a
  guarantee of fairness.

## Deployment

Deploy for free on [Streamlit Community Cloud](https://streamlit.io/cloud) —
point it at this repo and `app.py`. The `sentence-transformers` model will
download automatically on first run since Streamlit Cloud has internet
access.
