import random

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Users


@shared_task(bind=True)
def send_otp(self, email):
    """
    Sends an OTP to the specified email address and schedules its deletion.

    Args:
        self: The Celery task instance.
        email (str): The email address to send the OTP to.

    Raises:
        Exception: If there is an error sending the OTP or saving it to the database.
    """
    try:
        subject = "Your verification email"
        otp = random.randint(100000, 999999)
        message = f"your otp is {otp}"
        email_from = settings.EMAIL_HOST_USER

        # Retrieve the user object and update OTP
        user = Users.objects.get(email=email)
        user.otp = otp
        user.save()

        # Schedule task to delete OTP after 30 minutes
        delete_otp.apply_async(
            (user.id,), countdown=1800
        ) 

        send_mail(subject, message, email_from, [email])
        print(user.otp, str(user.username), "in send otp function")
    except Exception as e:
        print(f"Error sending OTP: {e}")


@shared_task
def delete_otp(id):
    """
    Deletes the OTP for the user with the specified ID.

    Args:
        id (int): The ID of the user whose OTP should be deleted.

    Raises:
        Exception: If there is an error retrieving the user or deleting the OTP.
    """
    try:
        user = Users.objects.get(id=id)
        user.otp = None
        user.save()
    except Exception as e:
        print(f"error deletin otp{e} eror")
