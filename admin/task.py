from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True)
def send_alert(self,subject,message,email_from,email_to):
    # operations
    try:
        print(subject,message,email_from,email_to)
        send_mail(subject,message,email_from,email_to)
        print('completed')
    except Exception as e:
        # Handle exceptions (e.g., email sending failure or user retrieval failure)
        print(f"Error sending OTP: {e}")