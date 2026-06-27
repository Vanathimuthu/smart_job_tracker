from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Application


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email"]


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "company",
            "role",
            "location",
            "salary",
            "job_description",
            "job_url",
            "apply_link",
            "status",
            "applied_date",
            "interview_date",
            "interview_reminder_date",
            "notes",
            "company_notes",
            "resume_summary",
            "skills_to_improve",
            "ats_score",
            "skill_gap_analysis",
            "ai_interview_questions",
        ]
        read_only_fields = ["id", "applied_date"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
