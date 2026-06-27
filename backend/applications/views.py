import os
import re
from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.serializers import RegisterSerializer
from .models import Application
from .serializers import ApplicationSerializer, UserSerializer


try:
    import openai
except ImportError:
    openai = None


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"user": UserSerializer(user).data}, status=201)


class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user).order_by("-applied_date")


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


class ResumeAnalysisView(APIView):
    permission_classes = [permissions.AllowAny]

    def _build_fallback_response(self, resume_text, job_description):
        resume_tokens = re.findall(r"[a-zA-Z]+", resume_text)
        job_tokens = re.findall(r"[a-zA-Z]+", job_description)

        resume_lookup = {token.lower(): token for token in resume_tokens}
        overlap = []
        seen = set()

        for token in job_tokens:
            key = token.lower()
            if len(key) > 3 and key in resume_lookup and key not in seen:
                overlap.append(resume_lookup[key])
                seen.add(key)

        overlap = sorted(overlap, key=lambda word: word.lower())
        recommendations = overlap[:5]
        ats_score = min(100, max(20, len(overlap) * 14))
        skill_gap_analysis = [
            skill for skill in sorted(set(job_tokens), key=lambda word: word.lower())
            if len(skill) > 3 and skill.lower() not in resume_lookup and skill.lower() not in {"the", "and", "with", "for", "experience", "role", "engineer"}
        ][:5]
        ai_interview_questions = [
            f"Tell me about your experience with {skill}." for skill in skill_gap_analysis[:3]
        ]

        if not recommendations:
            recommendations = ["Add job-specific keywords", "Highlight measurable achievements", "Tailor your summary to the role"]

        return {
            "match_score": ats_score,
            "ats_score": ats_score,
            "matched_skills": overlap[:8],
            "recommendations": recommendations,
            "skill_gap_analysis": skill_gap_analysis,
            "ai_interview_questions": ai_interview_questions,
            "ai_summary": (
                "Your resume shows solid overlap with the role, but the strongest opportunities are to strengthen "
                "the job-specific evidence and tailor your language to the employer's requirements."
            ),
        }

    def post(self, request):
        resume_text = request.data.get("resume_text") or ""
        job_description = request.data.get("job_description") or ""

        if not resume_text or not job_description:
            return Response({"detail": "resume_text and job_description are required"}, status=400)

        response_payload = self._build_fallback_response(resume_text, job_description)

        api_key = os.environ.get("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", None)
        if openai and api_key:
            try:
                client = openai.OpenAI(api_key=api_key)
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert resume reviewer and career coach. Return concise, actionable insights in plain English.",
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Analyze this resume against this job description. "
                                f"Resume: {resume_text}\n\nJob Description: {job_description}\n\n"
                                "Return JSON with keys: ats_score, matched_skills, recommendations, skill_gap_analysis, ai_interview_questions, ai_summary."
                            ),
                        },
                    ],
                    temperature=0.7,
                )
                content = completion.choices[0].message.content or ""
                import json

                parsed = json.loads(content)
                response_payload.update(parsed)
            except Exception:
                pass

        return Response(response_payload)
