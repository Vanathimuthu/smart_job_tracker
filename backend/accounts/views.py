from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import UserProfile
from .serializers import ForgotPasswordSerializer, RegisterSerializer, ResetPasswordSerializer, UserSerializer


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
        return Response(
            {
                "message": "Registration successful.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = UserProfile.objects.filter(email__iexact=email, is_active=True).first()
        response_payload = {
            "message": "If this email is registered, password reset details have been sent.",
        }

        if not user:
            if settings.DEBUG:
                response_payload["debug"] = {"email_registered": False}
            return Response(response_payload, status=status.HTTP_200_OK)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = request.build_absolute_uri(f"/api/accounts/reset-password/{uid}/{token}/")

        email_sent = False
        email_error = ""
        try:
            email_sent = bool(
                send_mail(
                    subject="Reset your password",
                    message=f"Use this link to reset your password: {reset_url}",
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            )
        except Exception as exc:
            email_error = str(exc)

        if settings.DEBUG:
            response_payload.update(
                {
                    "uid": uid,
                    "token": token,
                    "reset_url": reset_url,
                    "debug": {
                        "email_registered": True,
                        "email_sent": email_sent,
                        "email_error": email_error,
                        "from_email_configured": bool(getattr(settings, "DEFAULT_FROM_EMAIL", None)),
                    },
                }
            )

        return Response(response_payload, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uid=None, token=None):
        data = request.data.copy()
        if uid:
            data["uid"] = uid
        if token:
            data["token"] = token

        serializer = ResetPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
