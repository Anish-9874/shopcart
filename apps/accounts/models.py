from django.contrib.auth.models import User
from django.db import models


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="customerprofile"
    )
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True)

    def __str__(self):
        return self.user.username
