from celery import shared_task

from simple_django.accounts.models import EmailAddress


@shared_task
def send_verification_email(email_pk):
    email_address = EmailAddress.objects.get(pk=email_pk)
    email_address.send_verification_email()
