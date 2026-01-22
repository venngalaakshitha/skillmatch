from django.shortcuts import render

from resume_diagnostics_engine.skill_extractor import extract_explicit_skills
from resume_diagnostics_engine.role_recommender import suggest_roles


def recommend_roles(request):
    context = {}

    if request.method == "POST":
        resume_text = request.POST.get("resume_text", "")

        explicit_skills = extract_explicit_skills(resume_text)
        roles = suggest_roles(explicit_skills)

        context.update({
            "detected_skills": explicit_skills,
            "recommended_roles": roles,
        })

    return render(request, "recommend.html", context)


# Create your views here.
