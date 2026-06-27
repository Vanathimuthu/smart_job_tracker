from django.conf import settings
from django.db import models
from django.utils import timezone


class Job(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs")
    company = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    salary = models.CharField(max_length=255, blank=True, default="")
    job_url = models.URLField(blank=True, default="")
    apply_link = models.URLField(blank=True, default="")
    source = models.CharField(max_length=100, blank=True, default="")
    date_saved = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company} - {self.role or self.title}"


class CompanyResearch(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name="company_research")
    overview = models.TextField(blank=True, default="")
    products = models.TextField(blank=True, default="")
    tech_stack = models.TextField(blank=True, default="")
    recent_news = models.TextField(blank=True, default="")
    interview_tips = models.TextField(blank=True, default="")
    generated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Research for {self.job.company}"
