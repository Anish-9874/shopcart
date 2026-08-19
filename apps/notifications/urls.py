from django.urls import path

from . import views

app_name = "notifications"


urlpatterns = [
    path("", views.notification_list, name="list"),
    path("unread-count/", views.unread_count, name="unread_count"),
    path("<int:notification_id>/read/", views.mark_as_read, name="mark_as_read"),
]
