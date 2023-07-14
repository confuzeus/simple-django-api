from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core import cache
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken

from simple_django.accounts.managers import EmailAddressManager
from simple_django.accounts.types import UserAuthTokensDict


class User(AbstractUser):
    def update_login_timestamp(self):
        self.last_login = timezone.now()
        self.save()

    @property
    def email_verified(self):
        verified = False
        try:
            email_address = self.email_addresses.primary()
            if email_address.is_verified:
                verified = True
        except EmailAddress.DoesNotExist:
            verified = False

        return verified

    def get_auth_tokens(self, as_dict=True) -> UserAuthTokensDict | RefreshToken:
        refresh = RefreshToken.for_user(self)
        self.update_login_timestamp()
        if as_dict:
            return {"refresh": str(refresh), "access": str(refresh.access_token)}
        return refresh

    class Meta:
        ordering = ["-date_joined"]
        db_table = "users"


class EmailAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_addresses"
    )
    email = models.EmailField()
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EmailAddressManager()

    def set_as_primary(self):
        self.user.email = self.email
        self.user.save()
        self.is_primary = True
        self.save()

    @property
    def email_verification_cache_key(self):
        return f"email_verification_code_{self.id}"

    def set_verified(self):
        cache.cache.delete(self.email_verification_cache_key)
        self.is_verified = True
        self.save()

    def should_send_verification_email(self):
        if self.is_verified:
            return False

        cached_verification_code = cache.cache.get(self.email_verification_cache_key)

        return cached_verification_code is None

    def send_verification_email(self):
        if self.should_send_verification_email():
            verification_code = get_random_string(64).lower()
            ctx = {
                "user": self.user,
                "verification_code": verification_code,
                "confirmation_url": settings.EMAIL_CONFIRMATION_URL
                + f"?code={verification_code}",
            }
            html_email = render_to_string(
                "accounts/emails/confirm_email_address.html", ctx
            )
            text_email = render_to_string(
                "accounts/emails/confirm_email_address.txt", ctx
            )

            send_mail(
                subject="Email verification",
                message=text_email,
                html_message=html_email,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email],
            )
            cache.cache.set(
                self.email_verification_cache_key,
                verification_code,
                settings.EMAIL_VERIFICATION_EXPIRY.seconds,
            )

    def __str__(self):
        return self.email

    class Meta:
        db_table = "email_addresses"
        ordering = ["-updated_at"]
