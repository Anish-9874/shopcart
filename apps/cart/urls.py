from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart, name="cart"),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("update/<int:item_id>/<str:action>/", views.update_quantity, name="update_quantity"),
    path("remove/<int:item_id>/", views.remove_item, name="remove_item"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.my_orders, name="my_orders"),
]