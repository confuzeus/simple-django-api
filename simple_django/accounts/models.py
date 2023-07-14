from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    def update_login_timestamp(self):
        self.last_login = timezone.now()
        self.save()

    class Meta:
        ordering = ["-date_joined"]
        db_table = "users"
