from celery import shared_task
from django.core.mail import send_mail


# Task to notify the academy of admin approval via email.
# This function runs asynchronously using Celery.
# 
# Parameters:
# - self: Reference to the current task instance (used by Celery for task binding).
# - subject: Subject of the email.
# - message: Body of the email.
# - email_from: Sender's email address.
# - email_to: Recipient's email address(es) (can be a list).
#
# The function tries to send an email using Django's send_mail function. If an error occurs during the process,
# it prints an error message with the details.
@shared_task(bind=True)
def send_alert(self, subject, message, email_from, email_to):
    try:
        send_mail(subject, message, email_from, email_to)
    except Exception as e:
        print(f"Error sending OTP: {e}")
