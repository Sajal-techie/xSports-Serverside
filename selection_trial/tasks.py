from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True)
def send_status_mail(self,email,trial_name,message):
    try:
        print('in status mail',message,email,trial_name)
        subject = f"{trial_name} status updation"
        email_from = settings.EMAIL_HOST_USER
        send_mail(subject,message,email_from,[email])
    except Exception as e:
        print(f"Error sending status updation mail: {e}")
     
    print('our of celery task') 
        
        