from django.contrib import admin
from django.urls import include, path
from . import views
from accounts import views as acc_views

urlpatterns = [

    path("", include("chat.urls")),
    path("login/", acc_views.login_view, name="login"),
    path("signup/", acc_views.signup_view, name="signup"),

    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    path("customer-dashboard/", views.customer_dashboard, name="customer_dashboard"),
]