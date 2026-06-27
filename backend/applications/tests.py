from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Application


class ApplicationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="alice",
            email="alice@example.com",
            phone_number="9876543210",
            first_name="Alice",
            password="Secret123!",
        )

    def test_register_and_create_application(self):
        response = self.client.post(
            "/api/register/",
            {"username": "bob", "email": "bob@example.com", "password": "secret123"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/applications/",
            {
                "company": "Acme",
                "role": "Engineer",
                "status": "applied",
                "company_notes": "Strong product fit",
                "interview_reminder_date": "2026-07-01",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Application.objects.count(), 1)
        self.assertEqual(Application.objects.first().company_notes, "Strong product fit")

    def test_resume_analysis_returns_recommendations(self):
        response = self.client.post(
            "/api/analyze/",
            {
                "resume_text": "I have experience with Python, Django, PostgreSQL, and REST APIs.",
                "job_description": "We need a backend engineer with Python, Django, and PostgreSQL experience.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("recommendations", response.json())
        self.assertIn("Python", response.json()["recommendations"])
        self.assertIn("ats_score", response.json())
        self.assertIn("skill_gap_analysis", response.json())
        self.assertIn("ai_interview_questions", response.json())
        self.assertIn("ai_summary", response.json())
