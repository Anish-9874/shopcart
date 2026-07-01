from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect,render
from django.contrib import messages

from .models import Product, Cart, CartItem, Order,OrderItem



from django.contrib import messages

def add_to_cart(request, product_id):

    if not request.user.is_authenticated:
        messages.warning(request, "Please login first to add products to your cart.")
        return redirect("login")   # Replace "login" with your login URL name

    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, "Product added to cart successfully!")

    return redirect("cart")


@login_required
def cart(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    items = cart.items.all()

    total = sum(item.subtotal for item in items)

    return render(request, "cart.html", {
        "items": items,
        "total": total
    })




@login_required
def increase_quantity(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.quantity += 1
    item.save()

    return redirect("cart")





@login_required
def decrease_quantity(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")






@login_required
def remove_item(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.delete()

    return redirect("cart")





@login_required
def checkout(request):

    cart = Cart.objects.get(user=request.user)

    items = cart.items.all()

    total = sum(item.subtotal for item in items)

    order = Order.objects.create(
        user=request.user,
        total=total
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

        # Reduce stock
        item.product.stock -= item.quantity
        item.product.save()

    # Clear the cart
    items.delete()

    return redirect("home")