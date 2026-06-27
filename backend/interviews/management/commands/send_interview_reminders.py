from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from interviews.models import Interview
from interviews.services import send_interview_reminder_email


class Command(BaseCommand):
    help = 'Send email reminders for upcoming interviews (within 2 hours)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=2,
            help='Number of hours ahead to look for upcoming interviews (default: 2)',
        )

    def handle(self, *args, **options):
        hours = options.get('hours', 2)
        now = timezone.now()
        future = now + timedelta(hours=hours)

        # Get interviews scheduled in the next X hours that haven't had a reminder sent
        upcoming_interviews = Interview.objects.filter(
            scheduled_at__lte=future,
            scheduled_at__gt=now,
            reminder_email_sent=False
        )

        if not upcoming_interviews.exists():
            self.stdout.write(
                self.style.SUCCESS('No upcoming interviews to remind.')
            )
            return

        sent_count = 0
        failed_count = 0

        for interview in upcoming_interviews:
            try:
                send_interview_reminder_email(interview)
                interview.reminder_email_sent = True
                interview.save()
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Reminder sent for {interview.company} - {interview.role}'
                    )
                )
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Failed to send reminder for {interview.company}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {sent_count} reminders sent, {failed_count} failed.'
            )
        )
