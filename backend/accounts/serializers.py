import re

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from .models import UserProfile


def validate_strong_password(value):
    if len(value) < 8:
        raise serializers.ValidationError("Password must contain at least 8 characters.")
    if not re.search(r"[A-Z]", value):
        raise serializers.ValidationError("Password must include at least one capital letter.")
    if not re.search(r"[a-z]", value):
        raise serializers.ValidationError("Password must include at least one small letter.")
    if not re.search(r"\d", value):
        raise serializers.ValidationError("Password must include at least one number.")
    if not re.search(r"[^A-Za-z0-9]", value):
        raise serializers.ValidationError("Password must include at least one special character.")
    return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "username", "email", "first_name", "last_name", "phone_number")


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_username(self, value):
        value = value.strip()
        if not value.replace("_", "").isalnum():
            raise serializers.ValidationError("Username can contain only letters, numbers, and underscores.")
        if UserProfile.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already registered.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        if UserProfile.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_phone_number(self, value):
        digits = value.strip().replace(" ", "").replace("-", "")
        if digits.startswith("+91"):
            digits = digits[3:]
        elif digits.startswith("91") and len(digits) == 12:
            digits = digits[2:]

        if not digits.isdigit() or len(digits) != 10:
            raise serializers.ValidationError("Phone number must contain exactly 10 digits.")

        phone_number = f"+91{digits}"
        if UserProfile.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return phone_number

    def validate_password(self, value):
        return validate_strong_password(value)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        return UserProfile.objects.create_user(password=password, **validated_data)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_password(self, value):
        return validate_strong_password(value)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        try:
            user_id = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = UserProfile.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid reset link."})

        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError({"token": "Invalid or expired reset token."})

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["password"])
        user.save(update_fields=["password"])
        return user
