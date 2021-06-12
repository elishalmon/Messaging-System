from django.contrib.auth.models import User
from django.db import models


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", help_text="Sender of the message",
                               on_delete=models.CASCADE)
    reciever = models.ForeignKey(User, related_name="received_messages", help_text="Reciever of the message",
                                 on_delete=models.CASCADE)
    subject = models.CharField(max_length=128, help_text="Subject of the message")
    body = models.CharField(max_length=1024, help_text="Body of the message")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When message created")
    is_read = models.BooleanField(default=False)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_reciever = models.BooleanField(default=False)

    def __str__(self):
        return self.subject
