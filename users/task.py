from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import random
from .models import Users

@shared_task(bind=True)
def send_otp(self,email):
    # operations
    try:
        print('in send amil',str(self))
        subject = 'Your verification email'
        otp = random.randint(100000, 999999)
        message = f'your otp is {otp}'
        email_from = settings.EMAIL_HOST_USER
        user = Users.objects.get(email=email)
        user.otp = otp
        user.save()
        send_mail(subject, message, email_from,[email])
        print(user.otp,str(otp), str(user.username), 'in send otp function')
    except Exception as e:
        # Handle exceptions (e.g., email sending failure or user retrieval failure)
        print(f"Error sending OTP: {e}")