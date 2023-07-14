from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from simple_django.accounts.types import UserAuthTokensDict


class User(AbstractUser):
    def update_login_timestamp(self):
        self.last_login = timezone.now()
        self.save()

    def get_auth_tokens(self, as_dict=True) -> UserAuthTokensDict | RefreshToken:
        refresh = RefreshToken.for_user(self)
        self.update_login_timestamp()
        if as_dict:
            return {"refresh": str(refresh), "access": str(refresh.access_token)}
        return refresh

    class Meta:
        ordering = ["-date_joined"]
        db_table = "users"
