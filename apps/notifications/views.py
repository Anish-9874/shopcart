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

    if notification:
        notification.is_read = True
        notification.save(update_fields=["is_read"])

    return JsonResponse({"success": True})
