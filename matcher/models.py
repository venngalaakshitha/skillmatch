from django.contrib.auth.models import User
from django.db import models


class Resume(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='resumes'
    )

    # Uploaded resume
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True, default="")

    # Job description
    job_description = models.TextField(blank=True, null=True)

    # Core scores
    ats_score = models.FloatField(default=0, null=True, blank=True)
    jd_match_score = models.FloatField(default=0, null=True, blank=True)
    keyword_match_score = models.FloatField(default=0, null=True, blank=True)

    # Resume intelligence
    suggested_role = models.CharField(max_length=200, default="Software Developer")
    detected_skills = models.TextField(default="", blank=True)
    missing_skills = models.TextField(default="", blank=True)

    # Resume diagnosis
    overall_strength = models.CharField(max_length=50, blank=True, default="")
    ats_readability = models.CharField(max_length=50, blank=True, default="")
    strengths_summary = models.TextField(blank=True, default="")
    weaknesses_summary = models.TextField(blank=True, default="")
    suggestions_summary = models.TextField(blank=True, default="")

    # Analysis tracking
    analysis_status = models.CharField(
        max_length=50,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ]
    )

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']
        db_table = 'matcher_resume'

    def __str__(self):
        return f"Resume {self.id} - {self.suggested_role} ({self.ats_score}%)"

    def get_detected_skills_list(self):
        if self.detected_skills:
            return [skill.strip() for skill in self.detected_skills.split(',') if skill.strip()]
        return []

    def get_missing_skills_list(self):
        if self.missing_skills:
            return [skill.strip() for skill in self.missing_skills.split(',') if skill.strip()]
        return []

    def get_strengths_list(self):
        if self.strengths_summary:
            return [item.strip() for item in self.strengths_summary.split('|') if item.strip()]
        return []

    def get_weaknesses_list(self):
        if self.weaknesses_summary:
            return [item.strip() for item in self.weaknesses_summary.split('|') if item.strip()]
        return []

    def get_suggestions_list(self):
        if self.suggestions_summary:
            return [item.strip() for item in self.suggestions_summary.split('|') if item.strip()]
        return []