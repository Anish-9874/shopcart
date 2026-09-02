from django.urls import path

from . import views

app_name = "notifications"


urlpatterns = [
    path("notifications/", views.notification_list, name="list"),
    path("notifications/unread-count/", views.unread_count, name="unread_count"),
    path(
        "notifications/<int:notification_id>/read/",
        views.mark_as_read,
        name="mark_as_read",
    ),
]
