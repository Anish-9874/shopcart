from django.contrib import admin

from .models import CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "phone",
        "address",
    )

    list_filter = ("address",)

    search_fields = (
        "user__username",
        "user__email",
        "phone",
        "address",
    )

    autocomplete_fields = ("user",)

    list_select_related = ("user",)
