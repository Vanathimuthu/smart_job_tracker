from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .ai_client import AIServiceError
from .serializers import (
    CareerCoachSerializer,
    CompanyResearchSerializer,
    InterviewPrepSerializer,
    ResumeAnalysisSerializer,
    ResumeRewriteSerializer,
)
from .services import (
    analyze_resume,
    answer_career_question,
    generate_interview_questions,
    match_resume_to_job,
    research_company,
    rewrite_resume_section,
)


class ResumeAnalysisView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResumeAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payload = analyze_resume(
                serializer.validated_data["resume_text"],
                serializer.validated_data["job_description"],
            )
        except AIServiceError as exc:
            return Response({"detail": str(exc)}, status=getattr(exc, "status_code", status.HTTP_502_BAD_GATEWAY))
        return Response(payload, status=status.HTTP_200_OK)


class ResumeMatchView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResumeAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = match_resume_to_job(
                serializer.validated_data["resume_text"],
                serializer.validated_data["job_description"],
            )
        except AIServiceError as exc:
            return Response({"detail": str(exc)}, status=getattr(exc, "status_code", status.HTTP_502_BAD_GATEWAY))
        return Response(payload, status=status.HTTP_200_OK)


class ResumeRewriteView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResumeRewriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            rewritten_text = rewrite_resume_section(
                serializer.validated_data["section_text"],
                serializer.validated_data.get("target_role", ""),
            )
        except AIServiceError as exc:
            return Response({"detail": str(exc)}, status=getattr(exc, "status_code", status.HTTP_502_BAD_GATEWAY))
        return Response({"rewritten_text": rewritten_text}, status=status.HTTP_200_OK)


class InterviewPrepView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = InterviewPrepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = generate_interview_questions(
                serializer.validated_data.get("job_description", ""),
                serializer.validated_data.get("skills", []),
            )
        except AIServiceError as exc:
            return Response({"detail": str(exc)}, status=getattr(exc, "status_code", status.HTTP_502_BAD_GATEWAY))
        return Response(payload, status=status.HTTP_200_OK)


class CompanyResearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CompanyResearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payload = research_company(
                serializer.validated_data["company"],
                serializer.validated_data.get("job_description", ""),
            )
        except AIServiceError as exc:
            return Response({"detail": str(exc)}, status=getattr(exc, "status_code", status.HTTP_502_BAD_GATEWAY))
        return Response(payload, status=status.HTTP_200_OK)


class CareerCoachView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CareerCoachSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            answer = answer_career_question(
                serializer.validated_data["question"],
                serializer.validated_data.get("resume_text", ""),
                serializer.validated_data.get("job_description", ""),
            )
        except AIServiceError as exc:
            return Response({"detail": str(exc)}, status=getattr(exc, "status_code", status.HTTP_502_BAD_GATEWAY))
        return Response({"answer": answer}, status=status.HTTP_200_OK)
