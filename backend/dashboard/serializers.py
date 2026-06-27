from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    applications_count = serializers.IntegerField()
    applications_sent = serializers.IntegerField()
    interviews_scheduled = serializers.IntegerField()
    offers = serializers.IntegerField()
    rejections = serializers.IntegerField()
    average_ats_score = serializers.FloatField()
    jobs_count = serializers.IntegerField()
    resumes_count = serializers.IntegerField()
    interviews_count = serializers.IntegerField()
