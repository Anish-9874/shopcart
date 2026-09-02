import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from apps.notifications.services import send_notification
from apps.products.models import Product

from .forms import CheckoutForm
from .models import Cart, CartItem, Order, OrderItem

logger = logging.getLogger(__name__)


def _parse_quantity(raw, stock, default=1):
    """Safely parse a quantity from POST data and clamp it to [1, stock]."""
    try:
        quantity = int(raw)
    except (TypeError, ValueError):
        quantity = default
    if stock is not None:
        return max(1, min(quantity, stock))
    return max(1, quantity)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(request, f"{product.name} is out of stock.")
        return redirect("cart")

    # Previously this ignored the "quantity" field entirely and always
    # added exactly 1 unit, no matter what was selected in the qty stepper.
    quantity = _parse_quantity(request.POST.get("quantity"), product.stock)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        item.quantity = quantity
        item.save()
    else:
        new_quantity = item.quantity + quantity
        if new_quantity <= product.stock:
            item.quantity = new_quantity
            item.save()
        else:
            item.quantity = product.stock
            item.save()
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

            # A broken/misconfigured notification must never block checkout —
            # the order is already committed at this point, so a failure here
            # shouldn't turn into a 500 that strands the user before they
            # reach order_success.
            try:
                send_notification(
                    user=request.user,
                    title="Order Placed",
                    message=f"Your order #{order.id} has been placed successfully.",
                )
            except Exception:
                logger.exception(
                    "send_notification failed for order #%s (user_id=%s)",
                    order.id,
                    request.user.id,
                )

            return redirect("order_success")

        else:
            # Without this, an invalid form just re-renders checkout.html
            # with no visible feedback at all.
            messages.error(request, "Please fix the errors below and try again.")

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


@login_required
def buy_now(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(request, "Product is out of stock.")
        return redirect("product_list")

    # quantity comes from either the qty stepper on product_list.html
    # (first POST) or the hidden "quantity" field on buy_now.html
    # (final checkout POST).
    quantity = _parse_quantity(request.POST.get("quantity"), product.stock)

    # The first POST here (straight from product_list.html) only sends
    # "quantity" — no full_name/phone/address yet. Binding CheckoutForm to
    # that incomplete POST data would make every required field show
    # "This field is required." before the user has even seen the form,
    # so only bind it once the checkout fields have actually been submitted.
    is_checkout_submission = request.method == "POST" and "full_name" in request.POST

    if is_checkout_submission:

        form = CheckoutForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                product.refresh_from_db()

                if product.stock < quantity:
                    messages.error(
                        request,
                        f"Only {product.stock} unit(s) of {product.name} available.",
                    )
                    return redirect("product_list")

                order = Order.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data["full_name"],
                    phone=form.cleaned_data["phone"],
                    address=form.cleaned_data["address"],
                    payment_method=form.cleaned_data["payment_method"],
                    total=Decimal(product.price) * quantity,
                )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=quantity,
                    price=product.price,
                )

                Product.objects.filter(id=product.id).update(
                    stock=F("stock") - quantity
                )

            messages.success(request, "Order placed successfully.")

            try:
                send_notification(
                    user=request.user,
                    title="Order Placed",
                    message=f"Your order #{order.id} has been placed successfully.",
                )
            except Exception:
                logger.exception(
                    "send_notification failed for order #%s (user_id=%s)",
                    order.id,
                    request.user.id,
                )

            return redirect("order_success")

        else:
            messages.error(request, "Please fix the errors below and try again.")

    else:

        form = CheckoutForm()

    context = {
        "form": form,
        "product": product,
        "quantity": quantity,
        "total": product.price * quantity,
    }

    return render(request, "buy_now.html", context)


@login_required
def order_success(request):
    return render(request, "order_success.html")
