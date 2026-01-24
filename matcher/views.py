from django.shortcuts import render
from .models import Resume
from .services import extract_text_from_pdf

from resume_diagnostics_engine.section_detector import analyze_structure
from resume_diagnostics_engine.skill_extractor import (
    extract_explicit_skills,
    extract_inferred_skills
)
from resume_diagnostics_engine.role_recommender import suggest_roles
from resume_diagnostics_engine.ats_scorer import calculate_ats_score
from resume_diagnostics_engine.improvement_engine import generate_improvements
from resume_diagnostics_engine.jd_matcher import calculate_jd_match


def upload_resume(request):
    context = {}

    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        job_description = request.POST.get("job_description", "").strip()

        if not resume_file:
            context["warnings"] = ["No resume file uploaded."]
            return render(request, "upload.html", context)

        # ===== SAVE RESUME =====
        resume = Resume.objects.create(file=resume_file)

        # ===== EXTRACT TEXT (ONCE ONLY) =====
        text = extract_text_from_pdf(resume.file.path) or ""
        resume.extracted_text = text
        resume.save()

        # ===== SCANNED RESUME DETECTION =====
        if not text.strip():
            context.update({
                "warnings": [
                    "⚠️ Scanned resume detected (image-based PDF).",
                    "ATS systems cannot read images or scanned documents.",
                    "This resume contains no selectable text.",
                    "✅ Please upload one of the following formats:",
                    "• Text-based PDF exported from Word or Google Docs",
                    "• DOCX (Word document) converted to PDF",
                ]
            })
            return render(request, "upload.html", context)

        # ===== STRUCTURE ANALYSIS =====
        structure = analyze_structure(text) or {
            "has_skills": False,
            "has_experience": False,
            "has_education": False,
            "has_projects": False,
            "is_readable": False,
            "word_count": len(text.split())
        }

        explicit_skills = extract_explicit_skills(text)
        inferred_skills = extract_inferred_skills(text, explicit_skills)
        roles = suggest_roles(explicit_skills)

        # ===== ATS SCORE =====
        ats_score, score_breakdown = calculate_ats_score(
            structure,
            skill_count=len(explicit_skills)
        )

        # ===== IMPROVEMENT SUGGESTIONS =====
        improvements = generate_improvements(
            ats_score=ats_score,
            structure=structure,
            explicit_skills=explicit_skills
        )

        # ===== WARNINGS =====
        warnings = []
        if not explicit_skills:
            warnings.append("No explicit technical skills detected. Add a clear Skills section.")
        if not structure.get("has_experience"):
            warnings.append("Experience section missing. Add internships, training, or projects.")

        # ===== OPTIONAL JD MATCH =====
        jd_score = None
        missing_keywords = []

        if job_description:
            jd_score, missing_keywords = calculate_jd_match(
                resume_text=text,
                jd_text=job_description
            )

        # ===== CONTEXT =====
        context.update({
            "structure": structure,
            "ats_score": ats_score,
            "score_breakdown": score_breakdown,
            "detected_skills": explicit_skills,
            "inferred_skills": inferred_skills,
            "suggested_roles": roles,
            "warnings": warnings,
            "text_preview": text[:1200],
            "improvements": improvements,
            "jd_score": jd_score,
            "missing_keywords": missing_keywords,
        })

    return render(request, "upload.html", context)
