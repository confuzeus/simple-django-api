from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from simple_django.accounts.api.permissions import IsEmailAddressOwnerOrReadOnly
from simple_django.accounts.api.serializers import (
    EmailAddressSerializer,
    EmailPasswordLoginSerializer,
    EmailSignupSerializer,
    EmailVerificationSerializer,
    LoginWithGoogleSerializer,
    UserSerializer,
)
from simple_django.accounts.api.utils import set_refresh_token_cookie
from simple_django.accounts.models import EmailAddress

User = get_user_model()


class UserAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


@api_view(http_method_names=["POST"])
def signup_with_email(request):
    serializer = EmailSignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.save()
    response_data = {"access": data["tokens"]["access"], "user": data["user"]}
    response = Response(data=response_data)
    response = set_refresh_token_cookie(response, data["tokens"]["refresh"], 0)
    return response


@api_view(http_method_names=["POST"])
def login_with_email_password(request):
    auth_serializer = EmailPasswordLoginSerializer(data=request.data)
    auth_serializer.is_valid(raise_exception=True)
    auth_data = auth_serializer.save()
    data = {
        "access": auth_data["tokens"]["access"],
        "user": auth_data["user"],
    }

    response = Response(data=data)
    if auth_data["remember"]:
        refresh_token_expiry = settings.SESSION_COOKIE_AGE
    else:
        refresh_token_expiry = 0
    response = set_refresh_token_cookie(
        response,
        auth_data["tokens"]["refresh"],
        refresh_token_expiry,
    )
    return response


@api_view(http_method_names=["POST"])
def logout(request):
    response = Response()
    response.delete_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        "/",
        settings.REFRESH_TOKEN_COOKIE_DOMAIN,
        settings.REFRESH_TOKEN_COOKIE_SAMESITE,
    )
    return response


@api_view(http_method_names=["POST"])
def refresh_access_token(request):
    try:
        provided_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        if provided_token is None:
            provided_token = request.data.get("refresh", "")
        refresh = RefreshToken(provided_token)
    except TokenError:
        return Response(
            {
                "detail": "Session expired.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )
    return Response({"access": str(refresh.access_token)})


@api_view(http_method_names=["POST"])
def login_with_google(request):
    serializer = LoginWithGoogleSerializer(request.data)
    serializer.is_valid(raise_exception=True)
    tokens = serializer.save()
    response = Response(data={"access": tokens["access"]})
    response = set_refresh_token_cookie(response, tokens["refresh"])
    return response


class EmailAddressViewSet(
    RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet
):
    serializer_class = EmailAddressSerializer
    queryset = EmailAddress.objects.all()
    permission_classes = [IsAuthenticated, IsEmailAddressOwnerOrReadOnly]

    @action(detail=False, methods=["POST"])
    def verify_email(self, request):
        serializer = EmailVerificationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()
