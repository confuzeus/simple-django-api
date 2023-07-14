from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "simple_django.accounts"

    def ready(self):
        from . import models, signals

        post_save.connect(
            signals.create_email_address_after_registration, sender=get_user_model()
        )
        post_save.connect(
            signals.send_verification_email_on_create, sender=models.EmailAddress
        )
