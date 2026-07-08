from django.db import models
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

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.product.price * self.quantity
    



class Order(models.Model):

    STATUS = (
        ("Pending","Pending"),
        ("Packed","Packed"),
        ("Shipped","Shipped"),
        ("Delivered","Delivered"),
    )

    user = models.ForeignKey(User,on_delete=models.CASCADE)

    total = models.DecimalField(max_digits=10,decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)





class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )




