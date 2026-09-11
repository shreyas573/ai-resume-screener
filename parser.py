"""
parser.py
Extracts raw text from resumes/JDs in PDF, DOCX, or TXT format.
Kept intentionally simple for v1: pulls all text, no section detection.
"""
import io


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from a file given its bytes and filename."""
    name = filename.lower()
    try:
        if name.endswith(".pdf"):
            return _extract_pdf(file_bytes)
        elif name.endswith(".docx"):
            return _extract_docx(file_bytes)
        elif name.endswith(".txt"):
            return file_bytes.decode("utf-8", errors="ignore")
        else:
            return ""
    except Exception as e:
        return f"[PARSE_ERROR: {e}]"


def _extract_pdf(file_bytes: bytes) -> str:
    import pdfplumber
    text_chunks = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
    return "\n".join(text_chunks)


def _extract_docx(file_bytes: bytes) -> str:
    import docx
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def clean_text(text: str) -> str:
    """Basic whitespace normalization."""
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)
