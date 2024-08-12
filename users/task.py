import random

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Users


@shared_task(bind=True)
def send_otp(self, email):
    # operations
    try:
        subject = "Your verification email"
        otp = random.randint(100000, 999999)
        message = f"your otp is {otp}"
        email_from = settings.EMAIL_HOST_USER
        user = Users.objects.get(email=email)
        user.otp = otp
        user.save()
        delete_otp.apply_async(
            (user.id,), countdown=1800
        )  # delete otp from db after 30 mins
        send_mail(subject, message, email_from, [email])
        print(user.otp, str(user.username), "in send otp function")
    except Exception as e:
        print(f"Error sending OTP: {e}")


# to delete otp from db
@shared_task
def delete_otp(id):
    try:
        user = Users.objects.get(id=id)
        user.otp = None
        user.save()
    except Exception as e:
        print(f"error deletin otp{e} eror")
