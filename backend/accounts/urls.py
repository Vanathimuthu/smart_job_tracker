from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CustomTokenObtainPairView, ForgotPasswordView, RegisterView, ResetPasswordView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("reset-password/<str:uid>/<str:token>/", ResetPasswordView.as_view(), name="reset-password-confirm"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
