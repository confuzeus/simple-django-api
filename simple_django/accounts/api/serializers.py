from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from simple_django.accounts.models import EmailAddress
from simple_django.accounts.tasks import send_verification_email

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["email_verified"] = instance.email_verified
        return rep

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
        ]


class EmailSignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            raise ValidationError("A user with this email address already exists.")
        except User.DoesNotExist:
            pass
        return value

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        if validated_data["password"] != validated_data["confirm_password"]:
            raise ValidationError("Password and Confirm Password must be the same.")
        user = User(email=validated_data["email"], username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.full_clean()
        return {**validated_data, "user": user}

    def create(self, validated_data):
        user = validated_data["user"]
        user.save()
        user_serializer = UserSerializer(instance=user)
        return {"tokens": user.get_auth_tokens(), "user": user_serializer.data}


class EmailAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAddress
        exclude = ["user"]


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    def validate_code(self, value):
        user = self.context["request"].user
        try:
            email: EmailAddress = user.email_addresses.get(
                email=self.initial_data["email"]
            )
        except EmailAddress.DoesNotExist:
            raise ValidationError("Invalid email address.")

        cached_verification_code = cache.get(email.email_verification_cache_key)
        if cached_verification_code is None:
            send_verification_email.delay(email.id)
            raise ValidationError(
                "Verification code expired. Please check your email for a new one."
            )
        if cached_verification_code != value:
            raise ValidationError(
                "Invalid verification code. Please enter the correct one."
            )

        return value

    def create(self, validated_data):
        email_address: EmailAddress = self.context["request"].user.email_addresses.get(
            email=validated_data["email"]
        )
        email_address.set_verified()
        return email_address
