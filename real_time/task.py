from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from users.models import Users

from .models import Notification


@shared_task(bind=True)
def send_notification(self, notification_type, text, link, sender_id, receivers_list):
    """
    Celery task to send notifications to multiple users and broadcast them via WebSockets.
    
    Args:
        notification_type (str): The type of the notification (e.g., 'friend_request', 'message').
        text (str): The notification message to be sent.
        link (str): The link associated with the notification (e.g., URL to the relevant page).
        sender_id (int): The ID of the user sending the notification.
        receivers_list (list): A list of IDs of users who will receive the notification.
        
    This task does the following:
        1. Creates a notification entry in the database for each receiver.
        2. Sends the notification via WebSocket to each receiver's channel group.
    """

    print("in celery ", receivers_list, link, sender_id)

    # Get the channel layer for broadcasting WebSocket message
    channel_layer = get_channel_layer()
    sender = Users.objects.get(id=sender_id)

    for receiver_id in receivers_list:
        # Fetch the receiver user object
        receiver = Users.objects.get(id=receiver_id)

        # Create a Notification entry in the database for the receiver
        Notification.objects.create(
            receiver=receiver,
            sender=sender,
            notification_type=notification_type,
            text=text,
            link=link,
        )

        # Send the notification to the receiver's WebSocket channel group
        async_to_sync(channel_layer.group_send)(
            f"notification_{receiver_id}",  # Group name based on receiver ID
            {
                "type": "send_notification",  # The event type handled by the consumer
                "data": {
                    "type": notification_type,
                    "sender": sender.username,
                    "text": text,
                    "link": link,
                },
            },
        )
