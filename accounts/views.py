from django.http import HttpResponse
from django.contrib import messages

from django.shortcuts import render, redirect
from .forms import UserForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout

# Create your views here.
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.username == "anish":
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
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            print(form.errors)   # Add this
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')