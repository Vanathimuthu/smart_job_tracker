from django.conf import settings
from django.db import models


class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="resumes/", blank=True)
    content = models.TextField(blank=True, default="")
    target_role = models.CharField(max_length=255, blank=True, default="")
    skills = models.TextField(blank=True, default="")
    ats_score = models.IntegerField(default=0)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
