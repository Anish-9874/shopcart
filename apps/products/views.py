from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from apps.feedback.forms import FeedbackForm

from .forms import ProductForm
from .models import Category, Product


# ============================================================
# ADD PRODUCT
# ============================================================


def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            # Clear cache because product data has changed
            cache.clear()

            return redirect("add_product")

    else:
        form = ProductForm()

    return render(
        request,
        "add_product.html",
        {
            "form": form,
        },
    )


# ============================================================
# DELETE PRODUCT
# ============================================================


def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.delete()

        # Clear cache because product data has changed
        cache.clear()

        return redirect("see_product")

    return render(
        request,
        "delete_product.html",
        {
            "product": product,
        },
    )


# ============================================================
# PRODUCT LIST WITH SEARCH AND LOW-LEVEL CACHE
# ============================================================


def product_list(request):
    q = request.GET.get("q", "").strip()

    # Create a different cache key for every search query
    cache_key = f"products_{q}"

    # Try to get products from cache
    products = cache.get(cache_key)

    if products is None:
        print("Loading from database...")

        if q:
            products = list(
                Product.objects.filter(
                    Q(name__icontains=q)
                    | Q(description__icontains=q)
                )
            )

        else:
            products = list(
                Product.objects.all()
            )

        # Store products in cache for 5 minutes
        cache.set(
            cache_key,
            products,
            300,
        )

    else:
        print("Loading from cache...")

    return render(
        request,
        "product_list.html",
        {
            "products": products,
            "query": q,
        },
    )


# ============================================================
# SEE PRODUCTS WITH PAGINATION AND PER-VIEW CACHE
# ============================================================


@cache_page(60 * 15)
def see_product(request):
    products = Product.objects.all().order_by("-id")

    paginator = Paginator(products, 2)

    page_number = request.GET.get("page")

    page = paginator.get_page(page_number)

    return render(
        request,
        "see_product.html",
        {
            "products": page,
        },
    )


# ============================================================
# EDIT PRODUCT
# ============================================================


def edit_product(request, id):
    product = get_object_or_404(
        Product,
        id=id,
    )

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product,
        )

        if form.is_valid():
            form.save()

            # Clear cache because product data has changed
            cache.clear()

            return redirect("see_product")

    else:
        form = ProductForm(
            instance=product,
        )

    return render(
        request,
        "add_product.html",
        {
            "form": form,
        },
    )


# ============================================================
# CATEGORY LIST
# ============================================================


def category_list(request):
    categories = Category.objects.all()

    return render(
        request,
        "categories.html",
        {
            "categories": categories,
        },
    )


# ============================================================
# CATEGORY DETAILS
# ============================================================


def category(request, category_id):
    category = get_object_or_404(
        Category,
        id=category_id,
    )

    products = Product.objects.filter(
        category=category,
    )

    return render(
        request,
        "category_details.html",
        {
            "products": products,
            "category": category,
        },
    )


# ============================================================
# PRODUCT REVIEWS
# ============================================================


def product_review(request, id):
    product = get_object_or_404(
        Product,
        id=id,
    )

    if request.method == "POST":
        form = FeedbackForm(
            request.POST,
        )

        if form.is_valid():
            feedback = form.save(
                commit=False,
            )

            feedback.product = product
            feedback.user = request.user

            feedback.save()

            return redirect(
                "product_review",
                id=product.id,
            )

    else:
        form = FeedbackForm()

    feedbacks = product.feedbacks.all()

    return render(
        request,
        "feedback.html",
        {
            "product": product,
            "feedbacks": feedbacks,
            "form": form,
        },
    )