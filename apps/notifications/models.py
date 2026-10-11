from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
    )

    chat_message = models.ForeignKey(
        "chat.Message",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )

    order = models.ForeignKey(
        "cart.Order",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
    )

    text = models.CharField(max_length=255)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def day_bucket(self):
        notification_date = timezone.localtime(self.created_at).date()
        today = timezone.localdate()

        if notification_date == today:
            return "Today"

        if notification_date == today - timezone.timedelta(days=1):
            return "Yesterday"

        return notification_date.strftime("%B %d, %Y")

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.text}"
