from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.job_matcher import match_resume_to_job

from .models import Resume
from .serializers import ResumeSerializer
from .services import calculate_resume_ats_score


class ResumeListCreateView(generics.ListCreateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        ats_score = calculate_resume_ats_score(
            content=serializer.validated_data.get("content", ""),
            skills=serializer.validated_data.get("skills", ""),
            target_role=serializer.validated_data.get("target_role", ""),
            title=serializer.validated_data.get("title", ""),
        )
        serializer.save(user=self.request.user, ats_score=ats_score)


class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.ats_score = calculate_resume_ats_score(
            content=instance.content,
            skills=instance.skills,
            target_role=instance.target_role,
            title=instance.title,
        )
        instance.save(update_fields=["ats_score", "updated_at"])


class BestResumeRecommendationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        job_description = request.data.get("job_description", "")
        if not job_description:
            return Response(
                {"detail": "job_description is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        recommendations = []
        for resume in Resume.objects.filter(user=request.user):
            result = match_resume_to_job(resume.content or resume.skills, job_description)
            recommendations.append(
                {
                    "resume_id": resume.id,
                    "title": resume.title,
                    "ats_score": result["ats_score"],
                    "matched_skills": result["matched_skills"],
                    "missing_skills": result["missing_skills"],
                }
            )

        recommendations.sort(key=lambda item: item["ats_score"], reverse=True)
        return Response(
            {
                "best_resume": recommendations[0] if recommendations else None,
                "recommendations": recommendations,
            }
        )
