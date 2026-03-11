import re

def calculate_jd_match(resume_text: str, jd_text: str) -> tuple[float, list[str]]:
    # LOGIC: Clean and convert to Sets for O(1) lookup
    resume_words = set(resume_text.lower().split())
    jd_keywords = set(jd_text.lower().split())

    # LOGIC: The "Transparent Overlay" (Intersection)
    matched_skills = jd_keywords & resume_words  # Matches
    missing_skills = jd_keywords - resume_words  # Missing

    if not jd_keywords:
        return 0.0, []

    score = round((len(matched_skills) / len(jd_keywords)) * 100, 2)
    return score, list(missing_skills)
