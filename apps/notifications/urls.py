from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    # Customer notifications
    path(
        "notifications/",
        views.notification_list,
        name="list",
    ),
    # Admin notifications
    path(
        "admin-notifications/",
        views.admin_notification_list,
        name="admin_notifications",
    ),
    # Unread notification count
    path(
        "notifications/unread-count/",
        views.unread_count,
        name="unread_count",
    ),
    # Mark a notification as read
    path(
        "notifications/<int:notification_id>/read/",
        views.mark_as_read,
        name="mark_as_read",
    ),
]
