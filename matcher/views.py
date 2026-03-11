from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

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
# URL: "/" and "/upload/"
# ---------------------------------------------------
@login_required
def upload_resume(request):

    if request.method == "POST":

        resume_file = request.FILES.get("resume")
        job_description = request.POST.get("job_description", "")

        if not resume_file:
            messages.error(request, "Please upload a resume file.")
            return render(request, "upload.html")

        # Allow only PDF
        if not resume_file.name.lower().endswith(".pdf"):
            messages.error(request, "Only PDF files are allowed.")
            return render(request, "upload.html")

        # Save resume
        resume = Resume.objects.create(
            user=request.user,
            file=resume_file,
            job_description=job_description
        )

        try:
            extracted_text = extract_text_from_pdf(resume.file.path)
        except Exception:
            resume.delete()
            messages.error(request, "Could not process the PDF file.")
            return render(request, "upload.html")

        if not extracted_text:
            resume.delete()
            messages.error(request, "Failed to extract text from the resume.")
            return render(request, "upload.html")

        # ATS Score
        score, breakdown = realistic_ats_score(
            extracted_text,
            job_description
        )

        # Keyword Match
        keyword_score, matched_keywords = keyword_match_score(
            extracted_text,
            job_description
        )

        # Missing Skills
        missing = missing_skills(
            extracted_text,
            job_description
        )

        # Suggestions
        suggestions = resume_suggestions(score)

        # Save results
        resume.extracted_text = extracted_text
        resume.ats_score = score
        resume.save()

        messages.success(request, f"ATS Analysis Complete! Score: {score}%")

        return render(request, "results.html", {
            "resume": resume,
            "score": score,
            "breakdown": breakdown,
            "keyword_score": keyword_score,
            "matched_keywords": matched_keywords,
            "missing_skills": missing,
            "suggestions": suggestions
        })

    return render(request, "upload.html")


# ---------------------------------------------------
# View Resume ATS Report
# URL: /view/<resume_id>/
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

    context = {
        "resume": resume,
        "score": score,
        "breakdown": breakdown,
        "keyword_score": keyword_score,
        "matched_keywords": matched_keywords,
        "missing_skills": missing,
        "suggestions": suggestions
    }

    return render(request, "results.html", context)


# ---------------------------------------------------
# Resume History
# URL: /history/
# ---------------------------------------------------
@login_required
def history(request):

    resumes = Resume.objects.filter(
        user=request.user
    ).order_by("-uploaded_at")

    return render(request, "history.html", {"resumes": resumes})


# ---------------------------------------------------
# Delete Resume
# URL: /delete/<resume_id>/
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

    return redirect("history")


# ---------------------------------------------------
# User Signup
# URL: /signup/
# ---------------------------------------------------
def signup_view(request):

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth_login(request, user)

            return redirect("upload_resume")

    else:
        form = UserCreationForm()

    return render(request, "signup.html", {"form": form})


# ---------------------------------------------------
# User Login
# URL: /login/
# ---------------------------------------------------
def user_login(request):

    if request.method == "POST":

        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            auth_login(request, form.get_user())

            return redirect("upload_resume")

    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})