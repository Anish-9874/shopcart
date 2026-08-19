from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def send_notification(user, title, message, sender=None, chat_message=None):
    sender = sender or user
    text = f"{title}: {message}" if title else message

    notification = Notification.objects.create(
        recipient=user,
        sender=sender,
        text=text,
        chat_message=chat_message,
    )

    channel_layer = get_channel_layer()

    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "notification_message",
                "id": notification.id,
                "text": notification.text,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
            },
        )

    return notification
