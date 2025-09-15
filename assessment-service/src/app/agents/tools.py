def difficulty_estimator(text: str) -> dict:
    """
    Extremely simple heuristic for illustration.
    Replace with classifier or readability score as needed.
    """
    n = len((text or "").split())
    if n > 1200:
        return {"difficulty": "advanced"}
    if n > 500:
        return {"difficulty": "intermediate"}
    return {"difficulty": "beginner"}
