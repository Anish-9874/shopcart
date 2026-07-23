from django.http import HttpResponse
from django.shortcuts import redirect, render


def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin_dashboard")
        else:
            return redirect("customer_dashboard")

    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def loading(request):
    return render(request, "loading.html")
