from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resume
# Import the 'Brain' from your Service Layer
from .services import (
    extract_text_from_resume, 
    realistic_ats_score, 
    extract_skills, 
    suggest_role
)

@login_required
def upload_resume(request):
    """
    LOGIC: The Controller.
    IMAGINATION: Receives the file, hands it to the Service 'Factory', 
    and shows the result.
    """
    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        jd_text = request.POST.get("job_description", "")

        if not resume_file:
            messages.error(request, "Please upload a file.")
            return render(request, 'upload.html')

        # 1. PERSISTENCE: Save the file first
        resume_obj = Resume.objects.create(
            user=request.user,
            file=resume_file,
            job_description=jd_text
        )

        # 2. SERVICE CALL: Extract and Analyze (The Architecture Connection)
        # We call the functions from services.py here
        text = extract_text_from_resume(resume_obj.file.path)
        skills = extract_skills(text)
        score, breakdown = realistic_ats_score(text, jd_text, skills)
        role = suggest_role(skills)

        # 3. UPDATE DB: Save the results
        resume_obj.extracted_text = text
        resume_obj.ats_score = score
        resume_obj.suggested_role = role
        resume_obj.save()

        messages.success(request, "Analysis Complete!")
        return redirect('results', pk=resume_obj.pk)

    return render(request, 'upload.html')
