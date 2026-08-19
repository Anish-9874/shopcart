from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "sender",
        "recipient",
        "text",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "sender__username",
        "recipient__username",
        "text",
    )
