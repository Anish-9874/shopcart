from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db import transaction

from products.models import Product
from .models import Cart, CartItem, Order, OrderItem




def add_to_cart(request, product_id):

    if not request.user.is_authenticated:
        messages.warning(request, "Please login first to add products to your cart.")
        return redirect("login")

    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(request, f"{product.name} is out of stock.")
        return redirect("cart")

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created and item.quantity < product.stock:
        item.quantity += 1
        item.save()
    elif not created:
        messages.warning(request, f"Only {product.stock} unit(s) of {product.name} available.")

    return redirect("cart")





@login_required
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("product").all()
    total = sum(item.subtotal for item in items)
    return render(request, "cart.html", {"items": items, "total": total})





@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save()
    else:
        messages.warning(request, "No more stock available for this product.")

    return redirect("cart")





@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")





@login_required
def remove_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart")





@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.select_related("product").all()

    if not items:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    for item in items:
        if item.quantity > item.product.stock:
            messages.error(
                request,
                f"{item.product.name} only has {item.product.stock} left in stock."
            )
            return redirect("cart")

    with transaction.atomic():
        total = sum(item.subtotal for item in items)
        order = Order.objects.create(user=request.user, total=total)

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            item.product.stock -= item.quantity
            item.product.save()

        items.delete()

    messages.success(request, "Order placed successfully!")
    return redirect("my_orders")





@login_required
def my_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at")
        .prefetch_related("orderitem_set__product")
    )
    return render(request, "orders.html", {"orders": orders})