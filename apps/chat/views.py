import logging
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.notifications.services import send_notification

from .forms import MessageForm
from .models import ChatRoom, Message

logger = logging.getLogger(__name__)
User = get_user_model()


def broadcast_inbox_activity(room, message):
    """Notify connected admin inboxes about a new chat message."""
    try:
        channel_layer = get_channel_layer()

        if channel_layer is None:
            logger.warning("No channel layer configured for chat inbox.")
            return

        unread_count = Message.objects.filter(
            room=room,
            sender_id=room.customer_id,
            is_read=False,
        ).count()

        async_to_sync(channel_layer.group_send)(
            "admin_chat_inbox",
            {
                "type": "inbox_activity",
                "room_id": room.id,
                "customer_id": room.customer_id,
                "customer": room.customer.username,
                "message": message.text[:60],
                "created_at": message.created_at.isoformat(),
                "unread_count": unread_count,
                "activity_type": "new_message",
            },
        )

    except Exception:
        logger.exception(
            "Failed to broadcast inbox activity for room %s",
            room.id,
        )


@login_required
def customer_chat(request):
    room, _ = ChatRoom.objects.get_or_create(customer=request.user)

    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.room = room
            message.sender = request.user
            message.save()

            # Broadcast immediately to connected admin inboxes.
            broadcast_inbox_activity(room, message)

            # Notify active staff members.
            staff_users = User.objects.filter(
                is_staff=True,
                is_active=True,
            ).exclude(id=request.user.id)

            for staff_user in staff_users:
                try:
                    send_notification(
                        user=staff_user,
                        title="New Customer Message",
                        message=(f"{request.user.username} sent you a message."),
                        sender=request.user,
                        chat_message=message,
                    )
                except Exception:
                    logger.exception(
                        "Failed to notify staff user %s " "about chat message %s",
                        staff_user.id,
                        message.id,
                    )

            return redirect("customer_chat")

    else:
        form = MessageForm()

    messages = room.messages.select_related("sender").order_by("-created_at")[:50][::-1]

    return render(
        request,
        "customer_chatbox.html",
        {
            "room": room,
            "messages": messages,
            "form": form,
        },
    )


@user_passes_test(lambda user: user.is_staff)
def inbox(request):
    search = request.GET.get("search", "").strip()
    now = timezone.now()
    new_user_cutoff = now - timedelta(hours=24)

    customers = User.objects.filter(
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )

    if search:
        customers = customers.filter(
            Q(username__icontains=search) | Q(email__icontains=search)
        )

    rooms = []

    for customer in customers:
        room, _ = ChatRoom.objects.get_or_create(customer=customer)

        latest_message = (
            room.messages.select_related("sender").order_by("-created_at").first()
        )

        unread_count = room.messages.filter(
            sender_id=customer.id,
            is_read=False,
        ).count()

        last_activity = (
            latest_message.created_at if latest_message else customer.date_joined
        )

        if latest_message:
            activity_label = "Recent Conversation"
        elif customer.date_joined >= new_user_cutoff:
            activity_label = "New Signup"
        else:
            activity_label = "No Messages Yet"

        rooms.append(
            {
                "id": room.id,
                "customer": customer,
                "latest_message": latest_message,
                "unread_count": unread_count,
                "last_activity": last_activity,
                "activity_label": activity_label,
                "is_new_user": (
                    not latest_message and customer.date_joined >= new_user_cutoff
                ),
            }
        )

    rooms.sort(
        key=lambda item: item["last_activity"],
        reverse=True,
    )

    return render(
        request,
        "inbox.html",
        {
            "rooms": rooms,
            "search": search,
        },
    )


@user_passes_test(lambda user: user.is_staff)
def admin_chat(request, room_id):
    room = get_object_or_404(
        ChatRoom.objects.select_related("customer"),
        id=room_id,
    )

    # Opening a chat marks the customer's messages as read.
    if request.method == "GET":
        room.messages.filter(
            sender_id=room.customer_id,
            is_read=False,
        ).update(is_read=True)

    if request.method == "POST":
        form = MessageForm(request.POST)

        if form.is_valid():
            message = form.save(commit=False)
            message.room = room
            message.sender = request.user
            message.save()

            # Update the inbox for connected admins immediately.
            broadcast_inbox_activity(room, message)

            try:
                send_notification(
                    user=room.customer,
                    title="New Support Reply",
                    message="The support team replied to your message.",
                    sender=request.user,
                    chat_message=message,
                )
            except Exception:
                logger.exception(
                    "Failed to notify customer %s about chat message %s",
                    room.customer.id,
                    message.id,
                )

            return redirect("admin_chat", room_id=room.id)

    else:
        form = MessageForm()

    messages = room.messages.select_related("sender").order_by("-created_at")[:50][::-1]

    return render(
        request,
        "admin_chatbox.html",
        {
            "room": room,
            "messages": messages,
            "form": form,
        },
    )
