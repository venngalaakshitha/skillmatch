
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Resume(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='resumes'
    )
    
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField()
    
    # Analysis results
    ats_score = models.FloatField(default=0, null=True, blank=True)
    suggested_role = models.CharField(max_length=200, default="Software Developer")
    detected_skills = models.TextField(default="", blank=True)  # ← FIXED THIS
    job_description = models.TextField(blank=True, null=True)
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        db_table = 'matcher_resume'
    
    def __str__(self):
        return f"Resume {self.id} - {self.suggested_role} ({self.ats_score}%)"
    
    def get_detected_skills_list(self):
        """Convert comma-separated skills to list"""
        if self.detected_skills:
            return [skill.strip() for skill in self.detected_skills.split(',') if skill.strip()]
        return []
