from django.db import models
from users.models import Users

class Chat(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='send_message')
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE,related_name='receive_message')
    message = models.TextField(null=True)
    thread_name = models.CharField(max_length=255, null=True)
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.sender.username} - {self.receiver.username} - {self.message} "


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('message', 'Message'),
        ('friend_request', 'Friend Request'),
        ('friend_request_accept',"Friend Request Accepted"),
        ('follow', 'Follow'),
        ('new_post', 'New Post'),
        ('new_trial', 'New Trial')
    )
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="sent_notifications", null=True)
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="notifications", null=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, null=True)
    text = models.TextField(null=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Notification for {self.receiver.username} from {self.sender.username}: {self.text}"

