from django.conf import settings
from django.db import models


class Application(models.Model):
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("interview", "Interview"),
        ("offered", "Offered"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, default="")
    salary = models.CharField(max_length=255, blank=True, default="")
    job_description = models.TextField(blank=True, default="")
    job_url = models.URLField(blank=True, default="")
    apply_link = models.URLField(blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    applied_date = models.DateField(auto_now_add=True)
    interview_date = models.DateField(null=True, blank=True)
    interview_reminder_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    company_notes = models.TextField(blank=True)
    resume_summary = models.TextField(blank=True)
    skills_to_improve = models.TextField(blank=True)
    ats_score = models.IntegerField(default=0)
    skill_gap_analysis = models.TextField(blank=True)
    ai_interview_questions = models.TextField(blank=True)

    def __str__(self):
        return f"{self.company} - {self.role}"
