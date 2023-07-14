from functools import partial

from django.contrib.auth import get_user_model
from django.db import transaction

from simple_django.accounts.models import EmailAddress
from simple_django.accounts.tasks import send_verification_email

User = get_user_model()


def create_email_address_after_registration(*args, **kwargs):
    created = kwargs.get("created", False)

    if created:
        instance: User = kwargs.get("instance")
        email_address = EmailAddress(
            user=instance, email=instance.email, is_primary=True
        )
        email_address.save()


def send_verification_email_on_create(*args, **kwargs):
    created = kwargs.get("created", False)

    if created:
        instance: EmailAddress = kwargs.get("instance")
        transaction.on_commit(partial(send_verification_email.delay, instance.id))
