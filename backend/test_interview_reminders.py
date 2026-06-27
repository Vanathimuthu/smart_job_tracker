#!/usr/bin/env python
"""
Quick test script for interview reminders.
Run this to verify email configuration and create test data.
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_job_tracker.settings')
django.setup()

from django.contrib.auth import get_user_model
from interviews.models import Interview
from interviews.services import send_interview_reminder_email
from django.core.mail import send_mail
from django.utils import timezone

User = get_user_model()

def test_email_config():
    """Test basic email configuration."""
    print("=" * 60)
    print("TESTING EMAIL CONFIGURATION")
    print("=" * 60)
    
    try:
        send_mail(
            'Smart Job Tracker - Test Email',
            'If you received this, your email configuration is working!',
            'vanathivanathi52@gmail.com',
            ['vanathivanathi52@gmail.com'],
            fail_silently=False,
        )
        print("✓ Email test successful!")
        print("  Check your inbox for the test email.\n")
        return True
    except Exception as e:
        print(f"✗ Email test failed: {str(e)}\n")
        return False


def test_automatic_email():
    """Test automatic email sending via signals."""
    print("=" * 60)
    print("TESTING AUTOMATIC EMAIL SENDING (via Django Signals)")
    print("=" * 60)
    
    try:
        user = User.objects.first()
        if not user:
            print("✗ No users found in database!")
            print("  Please create a user account first.\n")
            return False
        
        # Create interview 45 minutes from now (triggers automatic email)
        scheduled_time = timezone.now() + timedelta(minutes=45)
        
        interview = Interview.objects.create(
            user=user,
            company='Facebook',
            role='Backend Engineer',
            scheduled_at=scheduled_time,
            platform='Zoom',
            meeting_link='https://zoom.us/j/12345',
            interviewer='Sarah Smith',
            notes='Automatic email test'
        )
        
        if interview.reminder_email_sent:
            print("✓ Automatic email sent!")
            print(f"  Company: {interview.company}")
            print(f"  Scheduled: {interview.scheduled_at}")
            print(f"  Email sent: {interview.reminder_email_sent}")
            print(f"  Check inbox for automatic reminder.\n")
            return True
        else:
            print("✗ Automatic email not sent")
            print(f"  Email flag: {interview.reminder_email_sent}\n")
            return False
            
    except Exception as e:
        print(f"✗ Failed: {str(e)}\n")
        return False


def test_far_future_interview():
    """Test that interviews far in future don't trigger immediate emails."""
    print("=" * 60)
    print("TESTING FUTURE INTERVIEW (> 24 hours)")
    print("=" * 60)
    
    try:
        user = User.objects.first()
        if not user:
            print("✗ No users found\n")
            return False
        
        # Create interview 7 days from now (should NOT trigger immediate email)
        scheduled_time = timezone.now() + timedelta(days=7)
        
        interview = Interview.objects.create(
            user=user,
            company='Microsoft',
            role='Cloud Architect',
            scheduled_at=scheduled_time,
            platform='Teams',
            meeting_link='https://teams.microsoft.com',
            interviewer='Mike Johnson'
        )
        
        if not interview.reminder_email_sent:
            print("✓ Correct behavior: No email for future interview")
            print(f"  Company: {interview.company}")
            print(f"  Scheduled: {interview.scheduled_at} (7 days away)")
            print(f"  Email will be sent by scheduled task 24 hours before\n")
            return True
        else:
            print("✗ Email should not be sent for interviews > 24 hours away\n")
            return False
            
    except Exception as e:
        print(f"✗ Failed: {str(e)}\n")
        return False


def test_management_command():
    """Test the management command."""
    print("=" * 60)
    print("TESTING MANAGEMENT COMMAND")
    print("=" * 60)
    
    from django.core.management import call_command
    from io import StringIO
    
    try:
        out = StringIO()
        call_command('send_interview_reminders', stdout=out)
        output = out.getvalue()
        print(output)
        return True
    except Exception as e:
        print(f"✗ Management command failed: {str(e)}\n")
        return False


def show_instructions():
    """Show next steps."""
    print("=" * 60)
    print("HOW TO USE YOUR INTERVIEW REMINDERS")
    print("=" * 60)
    print("""
🎯 AUTOMATIC EMAIL REMINDERS (Now working!):
   - Go to Interviews tab in the app
   - Create an interview scheduled for 1-2 hours from now
   - Email reminder is AUTOMATICALLY sent
   - Check your inbox!

🔔 BROWSER NOTIFICATIONS (No setup needed):
   - Automatically shown 2 hours before interview
   - Works in-app on Dashboard/Interviews tab

⏰ MANUAL TRIGGER (if needed):
   $ python manage.py send_interview_reminders

📅 SCHEDULED AUTO-REMINDERS:
   
   Windows (Task Scheduler):
   - Program: python manage.py send_interview_reminders
   - Run every: 30 minutes
   - Location: C:\\thaagam_task\\backend
   
   Linux/Mac (crontab):
   */30 * * * * cd /path/to/backend && python manage.py send_interview_reminders

⚙️ EMAIL TIMING:
   - Interviews within 24 hours: Email sent immediately when created
   - Interviews > 24 hours: Email sent by scheduled task 24 hours before
   - Past interviews: No email sent

✨ NEXT STEPS:
   1. Open the React app
   2. Go to Interviews tab
   3. Create an interview (use "Now" button for current time)
   4. Save it
   5. Check your email inbox - you should receive a reminder!

Need help? See: backend/interviews/REMINDERS_SETUP.md
""")


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║  SMART JOB TRACKER - INTERVIEW REMINDER SYSTEM TEST  ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    results = {
        'Email Configuration': test_email_config(),
        'Automatic Email (within 24h)': test_automatic_email(),
        'Future Interview (> 24h)': test_far_future_interview(),
        'Management Command': test_management_command(),
    }
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n")
    show_instructions()
