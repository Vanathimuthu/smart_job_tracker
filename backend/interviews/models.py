from django.conf import settings
from django.db import models


class Interview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interviews")
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    platform = models.CharField(max_length=100, blank=True, default="")
    meeting_link = models.URLField(blank=True, default="")
    interviewer = models.CharField(max_length=255, blank=True, default="")
    reminder_email_sent = models.BooleanField(default=False)
    browser_notification_sent = models.BooleanField(default=False)
    calendar_event_link = models.URLField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.role}"
