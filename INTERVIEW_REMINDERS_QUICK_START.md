# 🎉 Interview Reminders - Complete Setup Guide

## ✅ What's Now Working

### 1. **Automatic Email Reminders** (NEW!)
Emails are **automatically sent** when you create an interview in the React UI:
- ✓ Interview created within 24 hours → Email sent immediately
- ✓ Interview created > 24 hours away → Email sent 24 hours before
- ✓ Prevents duplicate emails automatically

### 2. **Browser Notifications**
No setup needed - shows automatically:
- ✓ Appears 2 hours before interview
- ✓ Shows on Dashboard or Interviews tab
- ✓ Includes meeting link status

### 3. **DateTime Picker Fix**
- ✓ Added "Now" button to auto-fill current time
- ✓ Prevents "12 o'clock" bug
- ✓ Shows correct times in Asia/Kolkata timezone

---

## 🚀 How to Use

### From the React App (Automatic):
1. Go to **Interviews** tab
2. Fill in interview details:
   - Company: `Google`
   - Role: `Senior Engineer`
   - Date and time: Click **"Now"** button → Auto-fills current time
   - Add other details (platform, link, interviewer)
3. Click **"Save interview"**
4. **✓ Email is automatically sent!** Check inbox

### Manual Command (Optional):
```bash
cd c:\thaagam_task\backend
python manage.py send_interview_reminders
```

### Scheduled Auto-Emails (Windows):
1. Open Task Scheduler
2. Create Basic Task:
   - Name: "Interview Reminders"
   - Trigger: Every 30 minutes
   - Program: `python.exe`
   - Arguments: `manage.py send_interview_reminders`
   - Start in: `C:\thaagam_task\backend`

### Scheduled Auto-Emails (Linux/Mac):
```bash
# Edit crontab
crontab -e

# Add this line (runs every 30 minutes)
*/30 * * * * cd /path/to/backend && python manage.py send_interview_reminders
```

---

## 📧 Email Details

**What you receive:**
- Company name
- Role
- Scheduled date/time
- Platform (Zoom, Google Meet, etc.)
- Meeting link
- Interviewer name
- Time until interview

**Sending rules:**
- New interviews (within 24h): Email sent immediately ✓
- Future interviews (>24h): Email sent 24h before
- Duplicate protection: Only 1 email per interview

---

## 🔍 Testing

```bash
# Run all tests
cd c:\thaagam_task\backend
python test_interview_reminders.py

# Expected output:
# ✓ PASS: Email Configuration
# ✓ PASS: Automatic Email (within 24h)
# ✓ PASS: Future Interview (> 24h)
# ✓ PASS: Management Command
```

---

## 📋 Files Created/Modified

**Created:**
- `interviews/signals.py` - Automatic email trigger
- `test_interview_reminders.py` - Test suite
- `interviews/management/commands/send_interview_reminders.py` - Management command
- `interviews/REMINDERS_SETUP.md` - Full setup guide

**Modified:**
- `interviews/apps.py` - Register signals
- `interviews/views.py` - Add response messages
- `interviews/services.py` - Email services
- `frontend/src/App.jsx` - UI improvements

---

## ✨ Next Steps

1. **Test in the app right now:**
   - Go to Interviews tab
   - Click "Now" to set current time
   - Save and check email inbox

2. **Optional: Set up automatic scheduling** (see instructions above)

3. **Enable browser notifications:**
   - Browser will ask for permission
   - Click "Allow" when prompted

---

## 🆘 Troubleshooting

**Not receiving emails?**
- Check spam folder
- Verify email configuration in `.env`
- Run test: `python test_interview_reminders.py`
- Check error logs

**Time showing wrong?**
- Click "Now" button to auto-fill
- Or manually type `HH:MM` format
- Times display in Asia/Kolkata timezone

**Browser notifications not showing?**
- Allow browser notifications in settings
- Check privacy settings
- Refresh the page

---

## 🎯 Key Features Summary

| Feature | Status | Setup | Trigger |
|---------|--------|-------|---------|
| Automatic Email | ✅ | None | Create interview |
| Browser Notification | ✅ | None | 2 hours before |
| Manual Email Trigger | ✅ | Optional | `python manage.py` |
| Scheduled Emails | ✅ | Optional | Cron/Task Scheduler |
| Correct Time Display | ✅ | None | Auto via timezone |
| "Now" Button | ✅ | None | Click button |

---

## 📞 Support

See detailed documentation:
- `backend/interviews/REMINDERS_SETUP.md` - Full guide
- `backend/test_interview_reminders.py` - Test script with examples

Enjoy your interview reminders! 🚀
