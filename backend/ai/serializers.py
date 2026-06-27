from rest_framework import serializers


class ResumeAnalysisSerializer(serializers.Serializer):
    resume_text = serializers.CharField()
    job_description = serializers.CharField()


class ResumeRewriteSerializer(serializers.Serializer):
    section_text = serializers.CharField()
    target_role = serializers.CharField(required=False, allow_blank=True)


class InterviewPrepSerializer(serializers.Serializer):
    job_description = serializers.CharField(required=False, allow_blank=True)
    skills = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
    )


class CompanyResearchSerializer(serializers.Serializer):
    company = serializers.CharField()
    job_description = serializers.CharField(required=False, allow_blank=True)


class CareerCoachSerializer(serializers.Serializer):
    question = serializers.CharField()
    resume_text = serializers.CharField(required=False, allow_blank=True)
    job_description = serializers.CharField(required=False, allow_blank=True)
