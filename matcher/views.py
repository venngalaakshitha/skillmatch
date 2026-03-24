from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

from .models import Resume
from .services import (
    realistic_ats_score,
    keyword_match_score,
    missing_skills,
    resume_suggestions,
    jd_match_score,
    skill_gap_analysis
)

import PyPDF2
from docx import Document


# ===================================================
# FILE TEXT EXTRACTION (PDF + DOCX)
# ===================================================
def extract_text(file):
    text = ""
    try:
        if file.name.lower().endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""

        elif file.name.lower().endswith(".docx"):
            doc = Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"

    except Exception:
        return None

    return text.strip()


# ===================================================
# HELPER: SCORE CLASS
# ===================================================
def get_score_class(score):
    if score >= 80:
        return "bg-success"
    elif score >= 60:
        return "bg-warning"
    return "bg-danger"


# ===================================================
# UPLOAD + ANALYSIS
# ===================================================
@login_required
def upload_resume(request):
    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        job_description = request.POST.get("job_description", "").strip()

        if not resume_file:
            messages.error(request, "Please upload a resume file.")
            return redirect("matcher:upload_resume")

        if not resume_file.name.lower().endswith((".pdf", ".docx")):
            messages.error(request, "Only PDF and DOCX files are allowed.")
            return redirect("matcher:upload_resume")

        resume = Resume.objects.create(
            user=request.user,
            file=resume_file,
            job_description=job_description
        )

        extracted_text = extract_text(resume_file)

        if not extracted_text:
            resume.delete()
            messages.error(request, "Failed to extract text from file.")
            return redirect("matcher:upload_resume")

        # Analysis
        ats_score, breakdown = realistic_ats_score(extracted_text, job_description)
        keyword_score, matched_keywords = keyword_match_score(extracted_text, job_description)
        missing = missing_skills(extracted_text, job_description)
        suggestions = resume_suggestions(ats_score)
        jd_score, jd_matched = jd_match_score(extracted_text, job_description)
        skill_gaps = skill_gap_analysis(extracted_text, job_description)

        # Save
        resume.extracted_text = extracted_text
        resume.ats_score = ats_score
        resume.save()

        messages.success(request, f"ATS Score: {ats_score}%")

        return render(request, "matcher/results.html", {
            "resume": resume,
            "ats_score": ats_score,
            "ats_class": get_score_class(ats_score),
            "breakdown": breakdown,
            "keyword_score": keyword_score,
            "matched_keywords": matched_keywords,
            "missing_skills": missing,
            "suggestions": suggestions,
            "jd_score": jd_score,
            "jd_class": get_score_class(jd_score),
            "jd_matched": jd_matched,
            "skill_gaps": skill_gaps,
        })

    return render(request, "matcher/upload.html")

from django.shortcuts import render

def index(request):
    return render(request, 'matcher/index.html')


# ===================================================
# VIEW REPORT
# ===================================================
@login_required
def view_resume_report(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    extracted_text = resume.extracted_text or ""

    ats_score, breakdown = realistic_ats_score(extracted_text, resume.job_description or "")
    keyword_score, matched_keywords = keyword_match_score(extracted_text, resume.job_description or "")
    missing = missing_skills(extracted_text, resume.job_description or "")
    suggestions = resume_suggestions(ats_score)
    jd_score, jd_matched = jd_match_score(extracted_text, resume.job_description or "")
    skill_gaps = skill_gap_analysis(extracted_text, resume.job_description or "")

    return render(request, "matcher/results.html", {
        "resume": resume,
        "ats_score": ats_score,
        "ats_class": get_score_class(ats_score),
        "breakdown": breakdown,
        "keyword_score": keyword_score,
        "matched_keywords": matched_keywords,
        "missing_skills": missing,
        "suggestions": suggestions,
        "jd_score": jd_score,
        "jd_class": get_score_class(jd_score),
        "jd_matched": jd_matched,
        "skill_gaps": skill_gaps,
    })


# ===================================================
# HISTORY
# ===================================================
@login_required
def history(request):
    resumes = Resume.objects.filter(user=request.user).order_by("-uploaded_at")
    return render(request, "matcher/history.html", {
        "resumes": resumes
    })


# ===================================================
# DELETE RESUME
# ===================================================
@login_required
@require_POST
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    resume.delete()
    messages.success(request, "Resume deleted successfully.")
    return redirect("matcher:history")


# ===================================================
# SIGNUP
# ===================================================
def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("matcher:upload_resume")
        else:
            messages.error(request, "Signup failed. Try again.")

    else:
        form = UserCreationForm()

    return render(request, "matcher/signup.html", {
        "form": form
    })


# ===================================================
# LOGIN
# ===================================================
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("matcher:upload_resume")
        else:
            messages.error(request, "Invalid username or password.")

    else:
        form = AuthenticationForm()

    return render(request, "matcher/login.html", {
        "form": form
    })