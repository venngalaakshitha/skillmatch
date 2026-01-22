from django.shortcuts import render
from resume_diagnostics_engine.skill_extractor import extract_explicit_skills
from resume_diagnostics_engine.constants import COMMON_SKILLS
from .logic import extract_skills_from_jd, calculate_match
from matcher.services import extract_text_from_pdf


def jd_matcher_view(request):
    context = {}

    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        jd_text = request.POST.get("job_description")

        resume_text = extract_text_from_pdf(resume_file)
        resume_skills = extract_explicit_skills(resume_text)

        jd_skills = extract_skills_from_jd(jd_text, COMMON_SKILLS)

        match_percent, matched, missing = calculate_match(
            resume_skills, jd_skills
        )

        context.update({
            "match_percent": match_percent,
            "matched_skills": matched,
            "missing_skills": missing,
        })

    return render(request, "jd_matcher/match.html", context)


# Create your views here.
