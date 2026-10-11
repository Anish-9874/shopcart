from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SignupForm
from .models import CustomerProfile
from .tasks import send_signup_message


# Create your views here.
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                return redirect("admin_dashboard")
            else:
                return redirect("customer_dashboard")

        else:
            messages.error(request, "Invalid login credentials. Please try again.")

    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def signup_view(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save()

            profile = user.customerprofile
            profile.phone = request.POST.get("phone", "")
            profile.address = request.POST.get("address", "")
            profile.save()

            send_signup_message.delay(user.id)
            login(request, user)

            return redirect("home")

    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def profile(request):
    profile = request.user.customerprofile

    return render(request, "profile.html", {"profile": profile})


@login_required
def edit_profile(request):
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Update User model
        request.user.email = request.POST.get("email")
        request.user.save()

        # Update CustomerProfile model
        profile.phone = request.POST.get("phone")
        profile.address = request.POST.get("address")

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES["profile_image"]

        profile.save()

        return redirect("profile")

    return render(request, "edit_profile.html", {"profile": profile})


def customer_profile(request, id):

    customer = get_object_or_404(User, id=id)
    profile = get_object_or_404(CustomerProfile, user=customer)

    return render(
        request,
        "my_customer.html",
        {
            "customer": customer,
            "profile": profile,
        },
    )


def customer_list(request):
    from datetime import timedelta

    from django.db.models import Q
    from django.utils import timezone

    search = request.GET.get("search", "").strip()
    sort = request.GET.get("sort", "newest")
    customer_filter = request.GET.get("filter", "all")

    # Get customers, excluding staff and superusers
    customers = User.objects.filter(
        is_staff=False,
        is_superuser=False,
    )

    # Search by username or email
    if search:
        customers = customers.filter(
            Q(username__icontains=search) | Q(email__icontains=search)
        )

    # Show users registered within the last 7 days
    if customer_filter == "new":
        recent_date = timezone.now() - timedelta(days=7)
        customers = customers.filter(date_joined__gte=recent_date)

    # Sorting options
    sort_options = {
        "az": "username",
        "za": "-username",
        "newest": "-date_joined",
        "oldest": "date_joined",
    }

    customers = customers.order_by(sort_options.get(sort, "-date_joined"))

    return render(
        request,
        "customer_list.html",
        {
            "customers": customers,
            "search": search,
            "sort": sort,
            "customer_filter": customer_filter,
        },
    )
