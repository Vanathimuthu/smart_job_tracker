from django.urls import path

from .views import (
    CareerCoachView,
    CompanyResearchView,
    InterviewPrepView,
    ResumeAnalysisView,
    ResumeMatchView,
    ResumeRewriteView,
)

urlpatterns = [
    path("analyze/", ResumeAnalysisView.as_view(), name="resume-analysis"),
    path("match/", ResumeMatchView.as_view(), name="resume-match"),
    path("rewrite/", ResumeRewriteView.as_view(), name="resume-rewrite"),
    path("interview-prep/", InterviewPrepView.as_view(), name="interview-prep"),
    path("company-research/", CompanyResearchView.as_view(), name="company-research"),
    path("career-coach/", CareerCoachView.as_view(), name="career-coach"),
]
