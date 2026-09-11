"""
evaluation.py
Computes precision@k against a hand-labeled evaluation set.

Expected labels format: a dict {filename: "fit" | "not_fit" | "maybe"}
Build this by manually reviewing 30-50 resume/JD pairs yourself (see README).
"""


def precision_at_k(ranked_filenames: list, labels: dict, k: int = 5) -> float:
    """
    ranked_filenames: resumes sorted by match score, best first.
    labels: {filename: "fit"/"not_fit"/"maybe"} - your manual ground truth.
    Returns the fraction of the top-k that you labeled "fit".
    """
    top_k = ranked_filenames[:k]
    if not top_k:
        return 0.0
    relevant = sum(1 for f in top_k if labels.get(f) == "fit")
    return relevant / len(top_k)
