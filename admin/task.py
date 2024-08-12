from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


# to notify academy of admin approval
@shared_task(bind=True)
def send_alert(self, subject, message, email_from, email_to):
    try:
        send_mail(subject, message, email_from, email_to)
    except Exception as e:
        print(f"Error sending OTP: {e}")
