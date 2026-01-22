from .constants import ROLE_SKILL_MAP

def suggest_roles(skills):
    matched_roles = []

    for role, required_skills in ROLE_SKILL_MAP.items():
        match_count = sum(skill in skills for skill in required_skills)

        if match_count >= 2:
            matched_roles.append(role)

    return matched_roles
