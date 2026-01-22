import re

def calculate_jd_match(resume_text, jd_text):
    resume_words = set(re.findall(r"[a-zA-Z]+", resume_text.lower()))
    jd_words = set(re.findall(r"[a-zA-Z]+", jd_text.lower()))

    common = resume_words.intersection(jd_words)

    if not jd_words:
        return 0, []

    score = int((len(common) / len(jd_words)) * 100)
    missing = sorted(jd_words - resume_words)

    return score, missing[:15]
