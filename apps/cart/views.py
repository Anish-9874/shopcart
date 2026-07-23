from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from apps.products.models import Product

from .forms import CheckoutForm
from .models import Cart, CartItem, Order, OrderItem


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(request, f"{product.name} is out of stock.")
        return redirect("cart")

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        if item.quantity < product.stock:
            item.quantity += 1
            item.save()
        else:
            messages.warning(
                request, f"Only {product.stock} unit(s) of {product.name} available."
            )

    return redirect("cart")


@login_required
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("product").all()
    total = sum(item.subtotal for item in items)
    return render(request, "cart.html", {"items": items, "total": total})


@login_required
def update_quantity(request, item_id, action):
    """Handles both increase and decrease so we don't need two near-identical views."""
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if action == "increase":
        if item.quantity < item.product.stock:
            item.quantity += 1
            item.save()
        else:
            messages.warning(request, "No more stock available for this product.")
    elif action == "decrease":
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

    cart, _ = Cart.objects.get_or_create(user=request.user)

    items = cart.items.select_related("product")

    if not items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    total = sum(item.subtotal for item in items)

    if request.method == "POST":

        form = CheckoutForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                # Check stock first
                for item in items:

                    if item.quantity > item.product.stock:

                        messages.error(
                            request,
                            f"{item.product.name} only has {item.product.stock} item(s) left.",
                        )

                        return redirect("cart")

                # Create Order
                order = Order.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data["full_name"],
                    phone=form.cleaned_data["phone"],
                    address=form.cleaned_data["address"],
                    payment_method=form.cleaned_data["payment_method"],
                    total=total,
                )

                # Create Order Items
                for item in items:

                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        quantity=item.quantity,
                        price=item.product.price,
                    )

                    # Reduce stock safely
                    Product.objects.filter(id=item.product.id).update(
                        stock=F("stock") - item.quantity
                    )

                # Clear cart
                items.delete()

            messages.success(request, "Order placed successfully!")

            return redirect("order_success")

    else:

        form = CheckoutForm()

    context = {
        "form": form,
        "items": items,
        "total": total,
    }

    return render(request, "checkout.html", context)


@login_required
def my_orders(request):

    orders = (
        Order.objects.filter(user=request.user)
        .order_by("-created_at")
        .prefetch_related("items__product")
    )

    return render(request, "orders.html", {"orders": orders})


from decimal import Decimal


@login_required
def buy_now(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(request, "Product is out of stock.")
        return redirect("products")

    if request.method == "POST":

        form = CheckoutForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                product.refresh_from_db()

                if product.stock <= 0:
                    messages.error(request, "Product is out of stock.")
                    return redirect("products")

                order = Order.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data["full_name"],
                    phone=form.cleaned_data["phone"],
                    address=form.cleaned_data["address"],
                    payment_method=form.cleaned_data["payment_method"],
                    total=Decimal(product.price),
                )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=1,
                    price=product.price,
                )

                Product.objects.filter(id=product.id).update(stock=F("stock") - 1)

            messages.success(request, "Order placed successfully.")

            return redirect("order_success")

    else:

        form = CheckoutForm()

    context = {
        "form": form,
        "product": product,
        "total": product.price,
    }

    return render(request, "buy_now.html", context)
