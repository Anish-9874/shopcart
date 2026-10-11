from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model

from apps.notifications.services import send_notification

from .models import ChatRoom, Message

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def receive_json(self, content):
        text = content.get("message")

        if not isinstance(text, str) or not text.strip():
            return

        text = text.strip()

        # Save the message and send existing notifications.
        message = await self.save_message(text)

        # Broadcast to everyone connected to this chat room.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message["text"],
                "sender": message["sender"],
                "created_at": message["created_at"],
            },
        )

        # Customer messages also update the admin inbox live.
        if message["is_customer"]:
            unread_count = await self.get_unread_count(
                message["room_id"],
                message["customer_id"],
            )

            await self.channel_layer.group_send(
                "admin_chat_inbox",
                {
                    "type": "inbox_activity",
                    "room_id": message["room_id"],
                    "customer_id": message["customer_id"],
                    "customer": message["customer"],
                    "message": message["text"][:60],
                    "created_at": message["created_at"],
                    "unread_count": unread_count,
                    "activity_type": "new_message",
                },
            )

    async def chat_message(self, event):
        await self.send_json(
            {
                "type": "chat",
                "message": event["message"],
                "sender": event["sender"],
                "created_at": event["created_at"],
            }
        )

    async def inbox_activity(self, event):
        # Used by the dedicated inbox consumer in the next step.
        await self.send_json(
            {
                "type": "inbox_activity",
                "room_id": event["room_id"],
                "customer_id": event["customer_id"],
                "customer": event["customer"],
                "message": event["message"],
                "created_at": event["created_at"],
                "unread_count": event["unread_count"],
                "activity_type": event["activity_type"],
            }
        )

    @database_sync_to_async
    def save_message(self, text):
        room = ChatRoom.objects.select_related("customer").get(id=self.room_name)

        message = Message.objects.create(
            room=room,
            sender=self.user,
            text=text,
        )

        self._notify_recipients(room, message)

        is_customer = room.customer_id == self.user.id

        return {
            "id": message.id,
            "room_id": room.id,
            "customer_id": room.customer_id,
            "customer": room.customer.username,
            "text": message.text,
            "sender": message.sender.username,
            "created_at": message.created_at.isoformat(),
            "is_customer": is_customer,
        }

    @database_sync_to_async
    def get_unread_count(self, room_id, customer_id):
        return Message.objects.filter(
            room_id=room_id,
            sender_id=customer_id,
            is_read=False,
        ).count()

    def _notify_recipients(self, room, message):
        """Notify conversation recipients other than the sender."""

        preview = message.text if len(message.text) <= 60 else f"{message.text[:57]}..."

        if room.customer_id == self.user.id:
            recipients = User.objects.filter(
                is_staff=True,
                is_active=True,
            ).exclude(id=self.user.id)
        else:
            recipients = [room.customer] if room.customer_id != self.user.id else []

        for recipient in recipients:
            try:
                send_notification(
                    user=recipient,
                    title=f"New message from {self.user.username}",
                    message=preview,
                    sender=self.user,
                    chat_message=message,
                )
            except Exception:
                import logging

                logging.getLogger(__name__).exception(
                    "Failed to send chat notification to user %s",
                    recipient.id,
                )


class AdminInboxConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]

        # Only authenticated staff may receive admin inbox events.
        if self.user.is_anonymous or not self.user.is_staff:
            await self.close()
            return

        self.group_name = "admin_chat_inbox"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def inbox_activity(self, event):
        await self.send_json(
            {
                "type": "inbox_activity",
                "room_id": event["room_id"],
                "customer_id": event["customer_id"],
                "customer": event["customer"],
                "message": event["message"],
                "created_at": event["created_at"],
                "unread_count": event["unread_count"],
                "activity_type": event["activity_type"],
            }
        )
