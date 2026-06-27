# Interview Reminders Setup Guide

## Overview

The Smart Job Tracker now includes two types of interview reminders:

1. **Browser Notifications** - In-app notifications when interviews are within 2 hours
2. **Email Reminders** - Email notifications sent via Django management command

## What Was Fixed

### Issue 1: Time Display Bug ✓
- **Problem**: Interviews were showing times after expected times (like "9:39 something")
- **Fix**: Updated to use explicit Asia/Kolkata timezone formatting with `Intl.DateTimeFormat`
- **Result**: All times now display correctly in your local timezone

### Issue 2: Missing Interview Reminders ✓
- **Problem**: No reminders were being sent for interviews
- **Solution**: 
  - Added browser notifications (shows 2 hours before interview)
  - Added email reminder system
  - Added management command for scheduling

## Browser Notifications (Automatic)

Browser reminders show automatically when you're on the dashboard/interviews page and an interview is within 2 hours.

**Requirements:**
- Browser notification permission must be granted
- Interview must be scheduled within the next 2 hours
- Page must be open (notifications will cache and show when page is refreshed)

## Email Reminders (Manual Setup Required)

Email reminders must be triggered via a management command or API endpoint. Choose one of the options below:

### Option 1: Manual Command (Quick Test)

Run this command to send reminders for all interviews in the next 2 hours:

```bash
python manage.py send_interview_reminders
```

To customize the hours ahead:

```bash
python manage.py send_interview_reminders --hours 24
```

### Option 2: Scheduled with Cron (Linux/Mac)

Add to your crontab to run every 30 minutes:

```bash
*/30 * * * * cd /path/to/thaagam_task/backend && python manage.py send_interview_reminders
```

Edit crontab:
```bash
crontab -e
```

### Option 3: Scheduled with Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (every 30 minutes)
4. Set action:
   - Program: `python.exe` (path to your Python executable)
   - Arguments: `manage.py send_interview_reminders`
   - Start in: `C:\thaagam_task\backend`

### Option 4: API Endpoint (External Scheduler)

Call this endpoint from any external service (like Zapier, IFTTT, etc.):

```
POST http://your-domain/api/interviews/send-reminders/
Authorization: Bearer <admin_token>
```

## Email Configuration

Reminders require email to be configured in Django. Check your `.env` file:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=1
```

For Gmail, use an [App Password](https://myaccount.google.com/apppasswords) instead of your regular password.

## Features

### Browser Notifications
- ✓ Automatic (no setup required)
- ✓ Shows 2 hours before interview
- ✓ Requires browser permission
- ✓ Includes meeting link status
- ✓ Can be clicked to open the app

### Email Reminders
- ✓ Includes interview details (company, role, platform, link)
- ✓ Shows time until interview
- ✓ Can be sent to multiple users
- ✓ Only sent once per interview
- ✓ Requires email configuration

## API Services

### Backend Services (interviews/services.py)

1. **send_interview_reminders()** - Send all due reminders
2. **send_interview_reminder_email(interview)** - Send reminder for specific interview
3. **get_upcoming_interviews(user, hours_ahead)** - Get upcoming interviews
4. **get_interviews_needing_reminders(user, minutes_before)** - Get interviews needing reminders

### Frontend Helpers (App.jsx)

1. **formatDateTimeIST(dateString)** - Format dates in Asia/Kolkata timezone
2. **getUpcomingInterviews(interviews)** - Get upcoming interviews with countdown
3. **getDueInterviews(interviews)** - Get interviews within 2 hours

## Testing

### Test Browser Notifications

1. Create an interview scheduled for 1 hour from now
2. Go to Interviews tab or Dashboard
3. Browser should ask for notification permission
4. You should see a notification card appear

### Test Email Reminders

```bash
# Create a test interview first, then:
python manage.py send_interview_reminders --hours 24

# Check console output for success/failure messages
```

## Troubleshooting

### Notifications Not Showing?
- Check if browser notifications are allowed in settings
- Check browser console for errors
- Ensure interview is within 2 hours from now
- Try refreshing the page

### Emails Not Sending?
- Check `.env` email configuration
- Test with: `python manage.py shell`
  ```python
  from django.core.mail import send_mail
  send_mail('Test', 'This is a test', 'from@example.com', ['to@example.com'])
  ```
- Check Django error logs
- Verify SMTP credentials are correct

### Times Still Wrong?
- Clear browser cache (Ctrl+Shift+Delete)
- Verify backend timezone: `echo $TZ` should show `Asia/Kolkata`
- Check if datetime input is set correctly before saving

## Database Notes

Interview reminder flags:
- `reminder_email_sent` - Tracks if email has been sent
- `browser_notification_sent` - For future use (currently browser handles locally)

These flags prevent duplicate reminders when running the command multiple times.

## Next Steps

1. ✅ Test browser notifications first (no setup needed)
2. ✅ Configure email in `.env` if you want email reminders
3. ✅ Set up a cron job or scheduler to run reminders regularly
4. ✅ Test with a future interview

Enjoy your interview reminders! 🎉
