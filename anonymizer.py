"""
anonymizer.py
Blind-screening preprocessing: strips PII (name, email, phone, and common
school/prestige signals) from resume text before it's embedded/scored.
This is the bias-mitigation feature - built into the pipeline, not bolted on.
"""
import re

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}")
LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/\S+", re.IGNORECASE)
URL_RE = re.compile(r"https?://\S+")

# Common name-line heuristic: first non-empty line of a resume is usually the name.
def anonymize(text: str) -> str:
    """Return a copy of text with direct identifiers removed."""
    lines = text.splitlines()
    if lines:
        # Assume first line is the candidate's name -> redact it.
        lines[0] = "[NAME REDACTED]"
    cleaned = "\n".join(lines)

    cleaned = EMAIL_RE.sub("[EMAIL REDACTED]", cleaned)
    cleaned = LINKEDIN_RE.sub("[LINK REDACTED]", cleaned)
    cleaned = URL_RE.sub("[LINK REDACTED]", cleaned)
    cleaned = PHONE_RE.sub("[PHONE REDACTED]", cleaned)
    return cleaned


def redact_institutions(text: str, institution_list) -> str:
    """Optionally strip named schools/universities to reduce prestige bias."""
    cleaned = text
    for inst in institution_list:
        cleaned = re.sub(re.escape(inst), "[INSTITUTION REDACTED]", cleaned, flags=re.IGNORECASE)
    return cleaned
