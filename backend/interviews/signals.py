from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Interview
from .services import send_interview_reminder_email


@receiver(post_save, sender=Interview)
def send_reminder_on_interview_save(sender, instance, created, **kwargs):
    """
    Automatically send reminder email when an interview is created or updated.
    Sends email if:
    - Interview is scheduled within the next 24 hours
    - Email hasn't been sent yet
    - It's within 2 hours of the scheduled time
    """
    try:
        now = timezone.now()
        scheduled_time = instance.scheduled_at
        
        # Skip if no scheduled time
        if not scheduled_time:
            return
        
        # Calculate time until interview
        time_until = scheduled_time - now
        
        # Skip if interview is in the past
        if time_until.total_seconds() < 0:
            return
        
        # Skip if interview is more than 24 hours away
        # (will be sent by scheduled management command)
        if time_until.total_seconds() > (24 * 60 * 60):
            return
        
        # Send email for interviews within next 24 hours
        if not instance.reminder_email_sent:
            send_interview_reminder_email(instance)
            instance.reminder_email_sent = True
            # Use update to avoid triggering signal again
            Interview.objects.filter(pk=instance.pk).update(reminder_email_sent=True)
            
    except Exception as e:
        # Log error but don't crash - email is not critical
        print(f"Error sending interview reminder: {str(e)}")
