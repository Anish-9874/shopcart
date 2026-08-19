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

        # Join room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        # Accept connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive_json(self, content):
        # Get message from browser
        text = content.get("message")

        if not text:
            return

        # Save message (also creates + pushes notifications)
        message = await self.save_message(text)

        # Send message to everyone in room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message.text,
                "sender": message.sender.username,
                "created_at": message.created_at.isoformat(),
            },
        )

    async def chat_message(self, event):
        # Send message to browser
        await self.send_json(
            {
                "type": "chat",
                "message": event["message"],
                "sender": event["sender"],
                "created_at": event["created_at"],
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

        return message

    def _notify_recipients(self, room, message):
        """Notify whoever is NOT the sender of this room's conversation."""

        preview = message.text if len(message.text) <= 60 else f"{message.text[:57]}..."

        if self.user_id_is_customer(room):
            # Customer sent a message -> notify every staff member
            recipients = User.objects.filter(is_staff=True).exclude(id=self.user.id)
        else:
            # Staff sent a message -> notify the customer
            recipients = [room.customer] if room.customer_id != self.user.id else []

        for recipient in recipients:
            send_notification(
                user=recipient,
                title=f"New message from {self.user.username}",
                message=preview,
                sender=self.user,
                chat_message=message,
            )

    def user_id_is_customer(self, room):
        return room.customer_id == self.user.id
