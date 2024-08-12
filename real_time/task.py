from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from users.models import Users


@shared_task(bind=True)
def send_notification(self, notification_type, text, link, sender_id, receivers_list):
    print("in celery ", receivers_list, link, sender_id)
    channel_layer = get_channel_layer()
    sender = Users.objects.get(id=sender_id)

    for receiver_id in receivers_list:
        receiver = Users.objects.get(id=receiver_id)
        Notification.objects.create(
            receiver=receiver,
            sender=sender,
            notification_type=notification_type,
            text=text,
            link=link,
        )

        #  send notificaion for each receiver
        async_to_sync(channel_layer.group_send)(
            f"notification_{receiver_id}",
            {
                "type": "send_notification",
                "data": {
                    "type": notification_type,
                    "sender": sender.username,
                    "text": text,
                    "link": link,
                },
            },
        )
