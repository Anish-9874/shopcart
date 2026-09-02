# from django.http import HttpResponse
from django.shortcuts import redirect, render

from apps.products.models import Category, Product


def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin_dashboard")
        else:
            return redirect("customer_dashboard")

    # NOTE: authenticated users are always redirected above, so this view
    # (and index.html) only ever renders for anonymous visitors.
    featured_products = Product.objects.filter(is_featured=True).order_by("-id")[:8]
    categories = Category.objects.all().order_by("name")[:8]

    context = {
        "featured_products": featured_products,
        "categories": categories,
    }

    return render(request, "index.html", context)


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def loading(request):
    return render(request, "loading.html")
