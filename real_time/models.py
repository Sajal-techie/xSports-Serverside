from django.db import models
from users.models import Users


class Chat(models.Model):
    """
    Model representing a chat message between two users.

    Attributes:
        sender (ForeignKey): The user who sends the message. Linked to the Users model.
        receiver (ForeignKey): The user who receives the message. Linked to the Users model.
        message (TextField): The content of the chat message.
        thread_name (CharField): The unique identifier for the chat thread between two users.
        date (DateTimeField): The timestamp when the message was created.
        read (BooleanField): A flag indicating whether the message has been read by the receiver.
    """
    sender = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="send_message"
    )
    receiver = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="receive_message"
    )
    message = models.TextField(null=True)
    thread_name = models.CharField(max_length=255, null=True)
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.sender.username} - {self.receiver.username} - {self.message} "


class Notification(models.Model):
    """
    Model representing a notification sent to a user.

    Attributes:
        NOTIFICATION_TYPES (tuple): A set of predefined notification types.
        sender (ForeignKey): The user who triggered the notification. Linked to the Users model.
        receiver (ForeignKey): The user who receives the notification. Linked to the Users model.
        notification_type (CharField): The type of notification, chosen from predefined types.
        text (TextField): The content of the notification message.
        link (CharField): A URL or reference link associated with the notification.
        seen (BooleanField): A flag indicating whether the notification has been seen by the receiver.
        created_at (DateTimeField): The timestamp when the notification was created.
    """
    NOTIFICATION_TYPES = (
        ("message", "Message"),
        ("friend_request", "Friend Request"),
        ("friend_request_accept", "Friend Request Accepted"),
        ("follow", "Follow"),
        ("new_post", "New Post"),
        ("new_trial", "New Trial"),
    )
    sender = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="sent_notifications", null=True
    )
    receiver = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="notifications", null=True
    )
    notification_type = models.CharField(
        max_length=50, choices=NOTIFICATION_TYPES, null=True
    )
    text = models.TextField(null=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Notification for {self.receiver.username} from {self.sender.username}: {self.text}"
