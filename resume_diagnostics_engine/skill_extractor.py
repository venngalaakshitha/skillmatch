import re
from .constants import COMMON_SKILLS, INFERRED_SKILLS, SKILLS_HEADERS


def extract_explicit_skills(text):
    text_lower = text.lower()

    skills_section = ""
    for header in SKILLS_HEADERS:
        pattern = rf"{header}[\s:]*([\s\S]*?)(\n\n|education|projects|experience)"
        match = re.search(pattern, text_lower)
        if match:
            skills_section = match.group(1)
            break

    if not skills_section:
        return []

    found = []
    for skill in COMMON_SKILLS:
        if skill in skills_section:
            found.append(skill)

    return sorted(set(found))


def extract_inferred_skills(text, explicit_skills):
    if explicit_skills:
        return []

    inferred = []
    for skill in INFERRED_SKILLS:
        if skill in text.lower():
            inferred.append(skill)

    return inferred
