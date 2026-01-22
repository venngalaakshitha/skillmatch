def generate_improvements(ats_score, structure, explicit_skills):
    improvements = []

    # ats_score is INT now (not tuple)
    if ats_score < 70:
        improvements.append(
            "Improve overall ATS score by adding clear section headings and more keywords."
        )

    if not structure.get("has_skills"):
        improvements.append(
            "Add a dedicated Skills section with clearly listed technologies."
        )

    if not structure.get("has_experience"):
        improvements.append(
            "Add an Experience section (internships, training, freelance, or projects)."
        )

    if len(explicit_skills) < 8:
        improvements.append(
            "List more explicit technical skills. ATS systems do not infer skills reliably."
        )

    if structure.get("word_count", 0) < 300:
        improvements.append(
            "Resume content seems short. Expand project descriptions with measurable impact."
        )

    return improvements
