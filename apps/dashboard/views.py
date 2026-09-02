from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.products.models import Category, Product


@login_required
def customer_dashboard(request):

    # Only this logged-in user's orders
    # Guest / anonymous user
    featured_products = Product.objects.filter(is_featured=True).order_by("-id")[:8]

    categories = Category.objects.all().order_by("name")[:8]

    context = {
        "featured_products": featured_products,
        "categories": categories,
    }

    return render(request, "customer_dashboard.html", context)


@login_required
def admin_dashboard(request):

    # Prevent normal customers from accessing admin dashboard
    if not request.user.is_staff:
        return redirect("customer_dashboard")

    return render(request, "admin_dashboard.html")
