from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.urls import reverse

from .models import Resume
from .services import (
    extract_text_from_pdf,
    realistic_ats_score,
    keyword_match_score,
    missing_skills,
    resume_suggestions
)


# ---------------------------------------------------
# Upload Resume + Run ATS Analysis
# ---------------------------------------------------
@login_required
def upload_resume(request):

    if request.method == "POST":

        resume_file = request.FILES.get("resume")
        job_description = request.POST.get("job_description", "").strip()

        if not resume_file:
            messages.error(request, "Please upload a resume file.")
            return redirect("matcher:upload_resume")

        # File validation
        if not resume_file.name.lower().endswith(".pdf"):
            messages.error(request, "Only PDF files are allowed.")
            return redirect("matcher:upload_resume")

        # Save resume
        resume = Resume.objects.create(
            user=request.user,
            file=resume_file,
            job_description=job_description
        )

        # Extract text safely
        try:
            extracted_text = extract_text_from_pdf(resume.file.path)
        except Exception:
            resume.delete()
            messages.error(request, "Failed to process PDF.")
            return redirect("matcher:upload_resume")

        if not extracted_text:
            resume.delete()
            messages.error(request, "Could not extract text from resume.")
            return redirect("matcher:upload_resume")

        # ----------------------------
        # ANALYSIS
        # ----------------------------
        score, breakdown = realistic_ats_score(
            extracted_text,
            job_description
        )

        keyword_score, matched_keywords = keyword_match_score(
            extracted_text,
            job_description
        )

        missing = missing_skills(
            extracted_text,
            job_description
        )

        suggestions = resume_suggestions(score)

        # Save results
        resume.extracted_text = extracted_text
        resume.ats_score = score
        resume.save()

        messages.success(request, f"ATS Score: {score}%")

        return render(request, "matcher/results.html", {
            "resume": resume,
            "score": score,
            "breakdown": breakdown,
            "keyword_score": keyword_score,
            "matched_keywords": matched_keywords,
            "missing_skills": missing,
            "suggestions": suggestions
        })

    return render(request, "matcher/upload.html")


# ---------------------------------------------------
# View Resume Report
# ---------------------------------------------------
@login_required
def view_resume_report(request, resume_id):

    resume = get_object_or_404(
        Resume,
        id=resume_id,
        user=request.user
    )

    score, breakdown = realistic_ats_score(
        resume.extracted_text,
        resume.job_description or ""
    )

    keyword_score, matched_keywords = keyword_match_score(
        resume.extracted_text,
        resume.job_description or ""
    )

    missing = missing_skills(
        resume.extracted_text,
        resume.job_description or ""
    )

    suggestions = resume_suggestions(score)

    return render(request, "matcher/results.html", {
        "resume": resume,
        "score": score,
        "breakdown": breakdown,
        "keyword_score": keyword_score,
        "matched_keywords": matched_keywords,
        "missing_skills": missing,
        "suggestions": suggestions
    })


# ---------------------------------------------------
# Resume History
# ---------------------------------------------------
@login_required
def history(request):

    resumes = Resume.objects.filter(
        user=request.user
    ).order_by("-uploaded_at")

    return render(request, "matcher/history.html", {
        "resumes": resumes
    })


# ---------------------------------------------------
# Delete Resume
# ---------------------------------------------------
@login_required
@require_POST
def delete_resume(request, resume_id):

    resume = get_object_or_404(
        Resume,
        id=resume_id,
        user=request.user
    )

    resume.delete()
    messages.success(request, "Resume deleted successfully.")

    return redirect("matcher:history")


# ---------------------------------------------------
# Signup
# ---------------------------------------------------
def signup_view(request):

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("matcher:upload_resume")

    else:
        form = UserCreationForm()

    return render(request, "matcher/signup.html", {
        "form": form
    })


# ---------------------------------------------------
# Login
# ---------------------------------------------------
def user_login(request):

    if request.method == "POST":

        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("matcher:upload_resume")

    else:
        form = AuthenticationForm()

    return render(request, "matcher/login.html", {
        "form": form
    })