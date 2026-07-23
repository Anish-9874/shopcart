from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MessageForm
from .models import ChatRoom


# ==========================
# Customer Chat
# ==========================
@login_required
def customer_chat(request):

    room, created = ChatRoom.objects.get_or_create(customer=request.user)

    if request.method == "POST":

        form = MessageForm(request.POST)

        if form.is_valid():

            message = form.save(commit=False)
            message.room = room
            message.sender = request.user
            message.save()

            return redirect("customer_chat")

    else:
        form = MessageForm()

    messages = room.messages.select_related("sender").order_by("-created_at")[:50][::-1]

    context = {
        "room": room,
        "messages": messages,
        "form": form,
    }

    return render(request, "customer_chatbox.html", context)


# ==========================
# Admin Inbox
# ==========================
@user_passes_test(lambda u: u.is_staff)
def inbox(request):

    rooms = ChatRoom.objects.select_related("customer").order_by("-id")

    context = {
        "rooms": rooms,
    }

    return render(request, "inbox.html", context)


# ==========================
# Admin Chat
# ==========================
@user_passes_test(lambda u: u.is_staff)
def admin_chat(request, room_id):

    room = get_object_or_404(ChatRoom, id=room_id)

    if request.method == "POST":

        form = MessageForm(request.POST)

        if form.is_valid():

            message = form.save(commit=False)
            message.room = room
            message.sender = request.user
            message.save()

            return redirect("admin_chat", room_id=room.id)

    else:
        form = MessageForm()

    messages = room.messages.select_related("sender").order_by("-created_at")[:50][::-1]

    context = {
        "room": room,
        "messages": messages,
        "form": form,
    }

    return render(request, "admin_chatbox.html", context)
