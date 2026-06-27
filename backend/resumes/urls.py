from django.urls import path

from .views import BestResumeRecommendationView, ResumeDetailView, ResumeListCreateView

urlpatterns = [
    path("", ResumeListCreateView.as_view(), name="resume-list-create"),
    path("recommend/", BestResumeRecommendationView.as_view(), name="resume-recommend"),
    path("<int:pk>/", ResumeDetailView.as_view(), name="resume-detail"),
]
