from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [path("user/", views.UserAPIView.as_view(), name="user")]
