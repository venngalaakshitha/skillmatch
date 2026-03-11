from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resume

# 1. ARCHITECTURE: The Clean Connection
# We import only what the view needs to "Delegate" the work.
from .services import (
    extract_text_from_pdf,   # Matches your services.py
    realistic_ats_score,     # Matches your services.py
)

@login_required
def upload_resume(request):
    """
    LOGIC: The Controller.
    IMAGINATION: A traffic cop directing data to the Service 'Factory'.
    """
    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        jd_text = request.POST.get("job_description", "")

        if not resume_file:
            messages.error(request, "❌ Please upload a valid file.")
            return render(request, 'upload.html')

        # 1. PERSISTENCE: Save the record first
        # Pro Tip: Saving first ensures we have a record to attach errors to if needed.
        resume_obj = Resume.objects.create(
            user=request.user,
            file=resume_file,
            job_description=jd_text
        )

        # 2. SERVICE CALL: Extraction (The Architecture Connection)
        # Logic: We use the Pydantic-validated service from services.py
        text = extract_text_from_pdf(resume_obj.file.path)
        
        # 3. DEFENSIVE PROGRAMMING: Validation Check
        if not text or len(text) < 50: # Standard resume usually > 50 chars
            resume_obj.delete() # Cleanup: Don't store "garbage" data
            messages.error(request, "❌ Analysis Failed: The PDF is unreadable, empty, or scanned.")
            return render(request, 'upload.html')

        # 4. ANALYTICS: Scoring (The O(1) Engine)
        # Logic: Hand off the clean text to our multi-factor scoring engine
        score, breakdown = realistic_ats_score(text, jd_text)

        # 5. DATA PERSISTENCE: Update the record
        resume_obj.extracted_text = text
        resume_obj.ats_score = score
        # Note: 'breakdown' can be stored in a JSONField or used in the template
        resume_obj.save()

        messages.success(request, f"✅ Analysis Complete! ATS Score: {score}%")
        
        # Redirect to a detail/result page (assuming you have a 'results' URL)
        return render(request, 'results.html', {
            'resume': resume_obj, 
            'breakdown': breakdown
        })

    return render(request, 'upload.html')

def resume_results(request, pk):
    """Simple view to display the stored analysis."""
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    return render(request, 'results.html', {'resume': resume})
