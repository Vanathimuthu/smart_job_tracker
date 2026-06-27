from rest_framework import serializers

from .models import CompanyResearch, Job


class CompanyResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyResearch
        fields = "__all__"
        read_only_fields = ("generated_at",)


class JobSerializer(serializers.ModelSerializer):
    company_research = CompanyResearchSerializer(read_only=True)

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = ("user", "date_saved", "created_at", "updated_at")
