from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")


@login_required
def customer_dashboard(request):
    return render(request, "customer_dashboard.html")


# Create your views here.
