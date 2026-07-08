from django.urls import path
from . import views

urlpatterns = [
    path("customer_chat/", views.customer_chat, name="customer_chat"),
    path("admin_chat/<int:room_id>/", views.admin_chat, name="admin_chat"),
    path("inbox/", views.inbox, name="inbox"),
]