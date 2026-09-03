from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .models import Notification


@login_required
def notification_list(request):
    notifications = (
        Notification.objects.filter(recipient=request.user)
        .select_related("sender", "chat_message")
        .order_by("-created_at")
    )

    return render(
        request, "notifications/notifications.html", {"notifications": notifications}
    )


@login_required
def unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    return JsonResponse({"count": count})


@login_required
def mark_as_read(request, notification_id):
    notification = Notification.objects.filter(
        id=notification_id, recipient=request.user
    ).first()

    was_unread = False

    if notification:
        was_unread = not notification.is_read
        if was_unread:
            notification.is_read = True
            notification.save(update_fields=["is_read"])

    # was_unread tells the client whether the badge count should actually
    # decrement (clicking an already-read notification shouldn't touch it).
    return JsonResponse({"success": bool(notification), "was_unread": was_unread})
