# Interview business logic belongs here.
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import Interview


def send_interview_reminders():
    """
    Send email reminders for interviews scheduled within the next 2 hours.
    This can be called by a periodic task (Celery, Django-Q, or APScheduler).
    """
    now = timezone.now()
    two_hours_from_now = now + timedelta(hours=2)
    
    # Get interviews scheduled in the next 2 hours that haven't had a reminder sent
    upcoming_interviews = Interview.objects.filter(
        scheduled_at__lte=two_hours_from_now,
        scheduled_at__gt=now,
        reminder_email_sent=False
    )
    
    for interview in upcoming_interviews:
        try:
            send_interview_reminder_email(interview)
            interview.reminder_email_sent = True
            interview.save()
        except Exception as e:
            print(f"Error sending reminder for interview {interview.id}: {str(e)}")


def send_interview_reminder_email(interview):
    """Send an email reminder for a specific interview."""
    user = interview.user
    
    subject = f"Reminder: Interview with {interview.company} for {interview.role}"
    
    time_until = interview.scheduled_at - timezone.now()
    hours = time_until.total_seconds() / 3600
    
    if hours > 1:
        time_str = f"{int(hours)} hours"
    else:
        minutes = time_until.total_seconds() / 60
        time_str = f"{int(minutes)} minutes"
    
    message = f"""Hi {user.first_name or 'there'},

This is a reminder about your upcoming interview!

Company: {interview.company}
Role: {interview.role}
Scheduled: {interview.scheduled_at.strftime('%Y-%m-%d %H:%M %Z')}
Time until interview: {time_str}
"""
    
    if interview.platform:
        message += f"Platform: {interview.platform}\n"
    
    if interview.meeting_link:
        message += f"Meeting link: {interview.meeting_link}\n"
    
    if interview.interviewer:
        message += f"Interviewer: {interview.interviewer}\n"
    
    message += f"""
Good luck with your interview!

Best regards,
Smart Job Tracker Team
"""
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def get_upcoming_interviews(user, hours_ahead=24):
    """Get upcoming interviews for a user within the specified hours."""
    now = timezone.now()
    future = now + timedelta(hours=hours_ahead)
    
    return Interview.objects.filter(
        user=user,
        scheduled_at__gt=now,
        scheduled_at__lte=future
    ).order_by('scheduled_at')


def get_interviews_needing_reminders(user, minutes_before=120):
    """Get interviews that need reminders (within specified minutes)."""
    now = timezone.now()
    reminder_time = now + timedelta(minutes=minutes_before)
    
    return Interview.objects.filter(
        user=user,
        scheduled_at__lte=reminder_time,
        scheduled_at__gt=now,
        reminder_email_sent=False
    )

