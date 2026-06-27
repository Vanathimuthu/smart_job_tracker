from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ApplicationDetailView,
    ApplicationListCreateView,
    CustomTokenObtainPairView,
    RegisterView,
    ResumeAnalysisView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("analyze/", ResumeAnalysisView.as_view(), name="resume-analysis"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("applications/", ApplicationListCreateView.as_view(), name="application-list-create"),
    path("applications/<int:pk>/", ApplicationDetailView.as_view(), name="application-detail"),
]
