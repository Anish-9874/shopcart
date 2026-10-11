from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def send_notification(
    user,
    title,
    message,
    sender=None,
    chat_message=None,
    order=None,
):
    """
    Create a notification for a user and send it over WebSocket.

    user: The notification recipient.
    title: Notification title.
    message: Notification message.
    sender: The user who triggered the notification.
    chat_message: Optional related chat message.
    order: Optional related order.
    """

    text = f"{title}: {message}" if title else message

    notification = Notification.objects.create(
        recipient=user,
        sender=sender or user,
        chat_message=chat_message,
        order=order,
        text=text,
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
