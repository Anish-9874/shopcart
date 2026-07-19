from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from apps.products.models import Product


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_cart_product"
            ),

            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="cartitem_quantity_gt_0"
            ),
        ]

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


# -----------------------------
# Order
# -----------------------------

class Order(models.Model):

    STATUS = (
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Packed", "Packed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )

    PAYMENT_METHOD = (
        ("COD", "Cash on Delivery"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    full_name = models.CharField(max_length=100)

    phone = models.CharField(max_length=20)

    address = models.TextField()

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD,
        default="COD"
    )

    payment_status = models.BooleanField(default=False)

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(total__gte=0),
                name="order_total_gte_0"
            ),
        ]

    def __str__(self):
        return f"Order #{self.id}"


# -----------------------------
# Order Item
# -----------------------------

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    product_name = models.CharField(max_length=200)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.price * self.quantity

    class Meta:
        constraints = [

            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_order_product"
            ),

            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="orderitem_quantity_gt_0"
            ),

            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="orderitem_price_gte_0"
            ),
        ]

    def __str__(self):
        return self.product_name