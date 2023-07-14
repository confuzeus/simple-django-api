from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
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
