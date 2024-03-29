from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

app_name = "accounts"

router = SimpleRouter()
router.register("email-addresses", views.EmailAddressViewSet)

urlpatterns = [
    path("user/", views.UserAPIView.as_view(), name="user"),
    path("email-signup/", views.signup_with_email, name="email-signup"),
    path(
        "email-password-login/",
        views.login_with_email_password,
        name="email-password-login",
    ),
    path("google-login/", views.login_with_google, name="google-login"),
    path("logout/", views.logout, name="logout"),
    path("refresh-token/", views.refresh_access_token, name="refresh-token"),
] + router.urls
