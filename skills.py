"""
skills.py
Extracts required skills from a job description and checks which ones
appear in a resume. This produces the human-readable "skill-gap" explanation
that sits alongside the similarity score.
"""
import re

# A reasonably broad starter dictionary covering common tech/data/business roles.
# Extend this list as needed for other domains.
SKILL_DICTIONARY = [
    "python", "java", "c++", "c#", "javascript", "typescript", "sql", "nosql",
    "r", "scala", "go", "rust", "html", "css",
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "data analysis", "data visualization", "statistics",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "xgboost", "random forest", "regression", "classification", "clustering",
    "power bi", "tableau", "excel", "streamlit",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github",
    "rest api", "flask", "django", "fastapi", "spark", "hadoop", "airflow",
    "etl", "data warehousing", "data engineering", "a/b testing",
    "communication", "leadership", "project management", "agile", "scrum",
]


def extract_required_skills(jd_text: str) -> list:
    """Return the subset of SKILL_DICTIONARY mentioned in the job description."""
    text_lower = jd_text.lower()
    found = []
    for skill in SKILL_DICTIONARY:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


def match_skills(resume_text: str, required_skills: list) -> dict:
    """Given a resume and a list of required skills, return matched/missing."""
    text_lower = resume_text.lower()
    matched, missing = [], []
    for skill in required_skills:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            matched.append(skill)
        else:
            missing.append(skill)
    return {"matched": matched, "missing": missing}
