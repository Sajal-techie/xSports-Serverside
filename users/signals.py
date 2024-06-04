from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Users
import random
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender = Users)
def send_otp_on_user_creation(sender,instance, created, **kwargs):
    print('increated signals ',instance)
    if created and not instance.is_superuser and not instance.is_staff:
        send_otp(instance.email)



def send_otp(email):
    try:
        print('in send amil')
        subject = 'Your verification email'
        otp = random.randint(100000, 999999)
        message = f'your otp is {otp}'
        email_from = settings.EMAIL_HOST_USER
        send_mail(subject, message, email_from,[email])
        user = Users.objects.get(email=email)
        user.otp = otp
        print(user.otp,otp, user.username, 'in send otp function')
        user.save()
    except Exception as e:
        # Handle exceptions (e.g., email sending failure or user retrieval failure)
        print(f"Error sending OTP: {e}")