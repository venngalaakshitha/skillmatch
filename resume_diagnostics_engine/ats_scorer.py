def calculate_ats_score(structure, skill_count=0):
    score = 0
    breakdown = {}

    # Structure (20)
    structure_score = sum([
        structure["has_skills"],
        structure["has_education"],
        structure["has_projects"],
        structure["is_readable"],
    ]) * 5
    breakdown["structure"] = structure_score
    score += structure_score

    # Skills (25)
    skill_score = min(skill_count * 3, 25)
    breakdown["skills"] = skill_score
    score += skill_score

    # Projects (20)
    project_score = 20 if structure["has_projects"] else 0
    breakdown["projects"] = project_score
    score += project_score

    # Experience penalty (ONLY −10)
    if not structure["has_experience"]:
        score -= 10
        breakdown["experience_penalty"] = -10
    else:
        breakdown["experience_penalty"] = 0

    # Word count (10)
    word_score = 10 if structure["word_count"] >= 200 else 5
    breakdown["readability"] = word_score
    score += word_score

    return min(max(score, 0), 100), breakdown
