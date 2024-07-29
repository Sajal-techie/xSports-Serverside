from django.db import models
from users.models import Users

class Chat(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='send_message')
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE,related_name='receive_message')
    message = models.TextField(null=True)
    thread_name = models.CharField(max_length=255, null=True)
    date = models.DateTimeField(auto_now_add=True)
    

    def __str__(self) -> str:
        return f"{self.sender.username} - {self.receiver.username} - {self.message} "
