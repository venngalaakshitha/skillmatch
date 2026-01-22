import re

def extract_skills_from_jd(jd_text, known_skills):
    jd_text = jd_text.lower()
    found = []

    for skill in known_skills:
        pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, jd_text):
            found.append(skill)

    return list(set(found))


def calculate_match(resume_skills, jd_skills):
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = resume_set & jd_set
    missing = jd_set - resume_set

    if not jd_set:
        return 0, [], []

    match_percent = int((len(matched) / len(jd_set)) * 100)

    return match_percent, list(matched), list(missing)
