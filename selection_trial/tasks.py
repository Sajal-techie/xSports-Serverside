from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


# to send notification mail if trial status is updated by academy
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
        

#  to send cancellation mail to users if academy cancelled trial
@shared_task(bind=True)
def send_trial_cancellation_mail(self,recipient_list,trial_name,academy_name,reason):
    try:
        print(' incelery to send cancellation mail',academy_name)
        subject = 'Trail cancelled'
        message = f"Dear player, \n\n we regret to inform you that the trial '{trial_name}' conducted by '{academy_name}' has been cancelled due to {reason}. Any payment processed will be refunded wihtin 3-7 days . \n Contact {academy_name} for further information. \n\n Best regards , \n PlayMaker"
        email_from = settings.EMAIL_HOST_USER
        send_mail(subject,message,email_from,recipient_list)
    except Exception as e:
        print(e,' erro sendingn calcellation mail')
        self.retry(exc=e,countdown=60,max_retries=3 )
    print('out of celery')