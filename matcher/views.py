import os
import docx
import PyPDF2

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.http import require_POST

from .models import Resume
from .services import (
    realistic_ats_score,
    keyword_match_score,
    missing_skills,
    resume_suggestions,
    jd_match_score,
    skill_gap_analysis,
    diagnose_resume,
    ai_resume_suggestions,
    extract_technical_skills,
    detect_ats_template_risk,
)


# =========================================
# BASIC PAGES
# =========================================

def index(request):
    return render(request, "matcher/index.html")


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("matcher:index")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("matcher:index")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, "matcher/signup.html", {"form": form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect("matcher:index")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect("matcher:index")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "matcher/login.html", {"form": form})


# =========================================
# FILE TEXT EXTRACTION
# =========================================

def extract_text(file_path):
    """
    Extract text from PDF or DOCX file.
    """
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()

        elif ext == ".docx":
            doc = docx.Document(file_path)
            return "\n".join(
                [para.text for para in doc.paragraphs if para.text.strip()]
            ).strip()

        return ""

    except Exception as e:
        print(f"Extraction error: {e}")
        return ""


# =========================================
# SCORE CLASS HELPER
# =========================================

def get_score_class(score):
    if score >= 80:
        return "bg-success"
    elif score >= 60:
        return "bg-warning text-dark"
    return "bg-danger"


# =========================================
# MAIN ANALYSIS
# =========================================

@login_required(login_url="matcher:login")
def upload_resume(request):
    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        job_description = request.POST.get("job_description", "").strip()

        if not resume_file:
            messages.error(request, "Please upload a resume file.")
            return redirect("matcher:upload_resume")

        file_ext = os.path.splitext(resume_file.name)[1].lower()
        if file_ext not in [".pdf", ".docx"]:
            messages.error(request, "Only PDF and DOCX files are supported.")
            return redirect("matcher:upload_resume")

        # Save uploaded file
        resume = Resume.objects.create(
            user=request.user,
            file=resume_file,
            job_description=job_description
        )

        # Extract resume text
        resume_text = extract_text(resume.file.path)

        if not resume_text.strip():
            resume.extracted_text = ""
            resume.analyzed_at = timezone.now()
            resume.save()

            messages.error(
                request,
                "Could not extract text from this resume. Please upload a cleaner PDF or DOCX file."
            )
            return redirect("matcher:upload_resume")

        # Run analysis
        ats_score, breakdown = realistic_ats_score(resume_text, job_description)
        keyword_score, matched_keywords = keyword_match_score(resume_text, job_description)
        missing = missing_skills(resume_text, job_description)
        jd_score, jd_matched = jd_match_score(resume_text, job_description)
        skill_gap = skill_gap_analysis(resume_text, job_description)
        suggestions = resume_suggestions(ats_score)
        ai_suggestions, improved_lines = ai_resume_suggestions(resume_text, job_description)
        resume_diagnosis = diagnose_resume(resume_text)
        detected_skills = extract_technical_skills(resume_text)
        ats_template_risk = detect_ats_template_risk(resume_text)

        # Save result summary
        resume.extracted_text = resume_text
        resume.ats_score = ats_score
        resume.detected_skills = ", ".join(detected_skills)
        resume.analyzed_at = timezone.now()
        resume.save()

        context = {
            "resume": resume,
            "ats_score": ats_score,
            "ats_class": get_score_class(ats_score),
            "breakdown": breakdown,
            "keyword_score": keyword_score,
            "matched_keywords": matched_keywords,
            "missing": missing,
            "suggestions": suggestions,
            "jd_score": jd_score,
            "jd_class": get_score_class(jd_score),
            "jd_matched": jd_matched,
            "skill_gap": skill_gap,
            "ai_suggestions": ai_suggestions,
            "improved_lines": improved_lines,
            "resume_text": resume_text,
            "resume_diagnosis": resume_diagnosis,
            "detected_skills": detected_skills,
            "ats_template_risk": ats_template_risk,
        }

        return render(request, "matcher/results.html", context)

    return render(request, "matcher/upload.html")


# =========================================
# HISTORY / REPORTS
# =========================================

@login_required(login_url="matcher:login")
def history(request):
    resumes = Resume.objects.filter(user=request.user).order_by("-uploaded_at")
    return render(request, "matcher/history.html", {"resumes": resumes})


@login_required(login_url="matcher:login")
def view_resume_report(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    resume_text = resume.extracted_text or ""
    job_description = resume.job_description or ""

    ats_score, breakdown = realistic_ats_score(resume_text, job_description)
    keyword_score, matched_keywords = keyword_match_score(resume_text, job_description)
    missing = missing_skills(resume_text, job_description)
    jd_score, jd_matched = jd_match_score(resume_text, job_description)
    skill_gap = skill_gap_analysis(resume_text, job_description)
    suggestions = resume_suggestions(ats_score)
    ai_suggestions, improved_lines = ai_resume_suggestions(resume_text, job_description)
    resume_diagnosis = diagnose_resume(resume_text)
    detected_skills = extract_technical_skills(resume_text)
    ats_template_risk = detect_ats_template_risk(resume_text)

    context = {
        "resume": resume,
        "ats_score": ats_score,
        "ats_class": get_score_class(ats_score),
        "breakdown": breakdown,
        "keyword_score": keyword_score,
        "matched_keywords": matched_keywords,
        "missing": missing,
        "suggestions": suggestions,
        "jd_score": jd_score,
        "jd_class": get_score_class(jd_score),
        "jd_matched": jd_matched,
        "skill_gap": skill_gap,
        "ai_suggestions": ai_suggestions,
        "improved_lines": improved_lines,
        "resume_text": resume_text,
        "resume_diagnosis": resume_diagnosis,
        "detected_skills": detected_skills,
        "ats_template_risk": ats_template_risk,
    }

    return render(request, "matcher/results.html", context)


@login_required(login_url="matcher:login")
@require_POST
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    resume.delete()
    messages.success(request, "Resume deleted successfully.")
    return redirect("matcher:history")