from django.contrib import messages
from .forms import SignupForm
from .models import CustomerProfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .models import CustomerProfile
# from .tasks import send_signup_message

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
    return render(request, 'login.html', {'form': form})


def signup_view(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save()

            profile = user.customerprofile
            profile.phone = request.POST.get("phone", "")
            profile.address = request.POST.get("address", "")
            profile.save()

           # send_signup_message.delay(user.id)
            login(request, user)

            return redirect("home")

    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('login')







@login_required
def profile(request):
    profile = request.user.customerprofile

    return render(request, "profile.html", {
        "profile": profile
    })


@login_required
def edit_profile(request):
    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user
    )

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

    return render(request, "edit_profile.html", {
        "profile": profile
    })



from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import CustomerProfile

def customer_profile(request, id):

    customer = get_object_or_404(User, id=id)
    profile = get_object_or_404(CustomerProfile, user=customer)

    return render(request, "my_customer.html", {
        "customer": customer,
        "profile": profile,
    })



def customer_list(request):
    search = request.GET.get("search", "")

    customers = User.objects.filter(is_staff=False)

    if search:
        customers = customers.filter(username__icontains=search)

    return render(request, "customer_list.html", {
        "customers": customers,
        "search": search,
    })


