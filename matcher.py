"""
matcher.py
Computes a match score between a job description and one or more resumes.

Primary method: Sentence-Transformers embeddings (semantic, understands meaning,
not just keywords) - requires internet access on first run to download the model.

Fallback method: TF-IDF + cosine similarity (scikit-learn) - works fully offline,
no model download needed. Used automatically if sentence-transformers isn't
installed or the model can't be downloaded (e.g. no internet access).
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

_model = None
_model_load_attempted = False


def _try_load_embedding_model():
    """Lazily attempt to load a Sentence-Transformers model. Cached after first try."""
    global _model, _model_load_attempted
    if _model_load_attempted:
        return _model
    _model_load_attempted = True
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        _model = None
    return _model


def get_active_method() -> str:
    """Report which matching method is currently active (for UI transparency)."""
    model = _try_load_embedding_model()
    return "semantic (Sentence-Transformers)" if model is not None else "keyword-weighted (TF-IDF)"


def score_resumes(jd_text: str, resume_texts: list) -> list:
    """
    Return a list of similarity scores (0-1) between the JD and each resume,
    in the same order as resume_texts.
    """
    model = _try_load_embedding_model()
    if model is not None:
        return _score_with_embeddings(model, jd_text, resume_texts)
    return _score_with_tfidf(jd_text, resume_texts)


def _score_with_embeddings(model, jd_text: str, resume_texts: list) -> list:
    jd_vec = model.encode([jd_text])
    resume_vecs = model.encode(resume_texts)
    sims = cosine_similarity(jd_vec, resume_vecs)[0]
    return [float(s) for s in sims]


def _score_with_tfidf(jd_text: str, resume_texts: list) -> list:
    corpus = [jd_text] + resume_texts
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf = vectorizer.fit_transform(corpus)
    jd_vec = tfidf[0:1]
    resume_vecs = tfidf[1:]
    sims = cosine_similarity(jd_vec, resume_vecs)[0]
    return [float(s) for s in sims]
