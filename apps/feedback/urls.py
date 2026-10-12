from django.urls import path

from apps.products.views import product_review

urlpatterns = [
    path(
        "product/<int:product_id>/",
        product_review,
        name="product_review",
    )
]
