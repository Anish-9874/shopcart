from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    customer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_room"
    )

    def __str__(self):
        return self.customer.username


class Message(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.text[:30]}"