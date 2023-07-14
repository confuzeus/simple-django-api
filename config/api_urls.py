from django.urls import include, path

app_name = "api"

handler500 = "rest_framework.exceptions.server_error"

handler400 = "rest_framework.exceptions.bad_request"

urlpatterns = [path("accounts/", include("simple_django.accounts.api.urls"))]
