from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('apps.dashboard.urls')),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/',views.profile, name='profile',),
    path('edit_profile/',views.edit_profile, name='edit_profile',),
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/<int:id>/", views.customer_profile, name="customer_profile"),

]