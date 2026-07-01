from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    CATEGORY_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Fashion', 'Fashion'),
        ('Grocery', 'Grocery'),
        ('Books', 'Books'),
    ]

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='Electronics'   # <-- Add this
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)   # New field
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return self.name

