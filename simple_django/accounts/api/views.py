from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from simple_django.accounts.api.serializers import EmailSignupSerializer, UserSerializer
from simple_django.accounts.api.utils import set_refresh_token_cookie

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
