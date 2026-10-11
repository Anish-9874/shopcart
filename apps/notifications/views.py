from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    notifications = (
        Notification.objects.filter(recipient=request.user)
        .select_related("sender", "chat_message", "order")
        .order_by("-created_at")
    )

    unread_count = notifications.filter(is_read=False).count()

    return render(
        request,
        "notifications/notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
@user_passes_test(lambda user: user.is_staff)
def admin_notification_list(request):
    notifications = (
        Notification.objects.filter(recipient=request.user)
        .select_related("sender", "chat_message", "order")
        .order_by("-created_at")
    )

    unread_count = notifications.filter(is_read=False).count()

    return render(
        request,
        "notifications/admin_notifications.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def unread_count(request):
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False,
    ).count()

    return JsonResponse({"count": count})


@login_required
@require_POST
def mark_as_read(request, notification_id):
    notification = Notification.objects.filter(
        id=notification_id,
        recipient=request.user,
    ).first()

    if notification is None:
        return JsonResponse(
            {"success": False, "was_unread": False},
            status=404,
        )

    was_unread = not notification.is_read

    if was_unread:
        notification.is_read = True
        notification.save(update_fields=["is_read"])

    return JsonResponse(
        {
            "success": True,
            "was_unread": was_unread,
        }
    )
