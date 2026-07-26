"""
checks/
Every checker in this package returns the same shape so app.py and the
frontend never need to special-case a check type:

    {
        "verdict": "safe" | "caution" | "danger",
        "risk_score": 0-100,
        "reasons": ["human-readable reason", ...],
    }

Each reason string is *why* points were added -- that list is what gets
rendered under "Why this verdict" on the frontend. Keeping the scoring
rule-based (instead of a black-box model) means every verdict is explainable
by construction, which matters more than accuracy for a student-facing
safety tool. See ml/README.md for the planned scikit-learn upgrade path.
"""


def verdict_from_score(score):
    """Shared thresholds so every checker maps score -> verdict the same way."""
    if score >= 60:
        return "danger"
    if score >= 30:
        return "caution"
    return "safe"


def build_result(score, reasons):
    score = max(0, min(100, score))
    if not reasons:
        reasons = ["No red flags matched any of our heuristics."]
    return {
        "verdict": verdict_from_score(score),
        "risk_score": score,
        "reasons": reasons,
    }
