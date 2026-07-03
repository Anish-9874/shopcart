from django.contrib import admin
from django.urls import include, path
from . import views


urlpatterns = [
    path('', include('dashboard.urls')),
    path('', include('chat.urls')),
    path('add_product/', views.add_product, name='add_product'),
    path('delete_product/<int:id>/', views.delete_product, name='delete_product'),
    path('see_product/', views.see_product, name='see_product'),
    path('products/', views.product_list, name='product_list'),
    path('category/', views.category_list, name='category_list'),
    path('category/<str:category_name>/', views.category, name='category'),
    path('edit_product/<int:id>/', views.edit_product, name='edit_product'),
]