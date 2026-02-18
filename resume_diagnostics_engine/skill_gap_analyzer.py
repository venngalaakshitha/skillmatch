from .skill_extractor import extract_explicit_skills


def analyze_skill_gap(resume_text: str, jd_text: str):
    """
    Compares resume skills with job description skills
    Returns:
    - match_percentage (int)
    - missing_skills (list)
    - matched_skills (list)
    """

    if not resume_text or not jd_text:
        return 0, [], []

    resume_skills = set(
        skill.lower() for skill in extract_explicit_skills(resume_text)
    )

    jd_skills = set(
        skill.lower() for skill in extract_explicit_skills(jd_text)
    )

    if not jd_skills:
        return 0, [], []

    matched_skills = resume_skills.intersection(jd_skills)
    missing_skills = jd_skills - resume_skills

    match_percentage = int(
        (len(matched_skills) / len(jd_skills)) * 100
    )

    return match_percentage, sorted(missing_skills), sorted(matched_skills)
