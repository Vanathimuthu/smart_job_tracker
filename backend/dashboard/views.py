from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.models import Application
from interviews.models import Interview
from jobs.models import Job
from resumes.models import Resume


class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        applications = Application.objects.filter(user=request.user)
        resumes = Resume.objects.filter(user=request.user)
        ats_scores = list(applications.exclude(ats_score=0).values_list("ats_score", flat=True))
        ats_scores += list(resumes.exclude(ats_score=0).values_list("ats_score", flat=True))

        return Response(
            {
                "applications_count": applications.count(),
                "applications_sent": applications.count(),
                "interviews_scheduled": applications.filter(status="interview").count()
                + Interview.objects.filter(user=request.user, scheduled_at__isnull=False).count(),
                "offers": applications.filter(status="offered").count(),
                "rejections": applications.filter(status="rejected").count(),
                "average_ats_score": round(sum(ats_scores) / len(ats_scores), 2) if ats_scores else 0,
                "jobs_count": Job.objects.filter(user=request.user).count(),
                "resumes_count": resumes.count(),
                "interviews_count": Interview.objects.filter(user=request.user).count(),
            }
        )
