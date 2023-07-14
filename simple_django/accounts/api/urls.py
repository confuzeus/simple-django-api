from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

app_name = "accounts"

router = SimpleRouter()
router.register("email-addresses", views.EmailAddressViewSet)

urlpatterns = [
    path("user/", views.UserAPIView.as_view(), name="user"),
    path("email-signup/", views.signup_with_email, name="email-signup"),
] + router.urls
