from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import cache_page

from apps.feedback.forms import FeedbackForm

from .forms import ProductForm
from .models import Category, Product

# ============================================================
# ADD PRODUCT
# ============================================================


@staff_member_required
def add_product(request):
    category_id = request.GET.get("category") or request.POST.get("category_id")
    next_url = request.GET.get("next") or request.POST.get("next")

    selected_category = None

    if category_id:
        selected_category = get_object_or_404(Category, pk=category_id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            cache.clear()

            # Return to the page that opened the form, if safe
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect("see_product")

    else:
        form = ProductForm(
            initial={
                "category": selected_category,
            }
        )

    return render(
        request,
        "add_product.html",
        {
            "form": form,
            "next_url": next_url,
            "selected_category": selected_category,
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
                    Q(name__icontains=q) | Q(description__icontains=q)
                )
            )

        else:
            products = list(Product.objects.all())

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


# ============================================================
# SEE PRODUCTS WITH SEARCH, FILTERS, SORTING AND PAGINATION
# ============================================================


@staff_member_required
@cache_page(60 * 15)
def see_product(request):
    # Read filter values from the query string.
    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    stock = request.GET.get("stock", "").strip()
    sort = request.GET.get("sort", "newest").strip()

    # Start with all products.
    products = Product.objects.select_related("category").all()

    # Search by product name, description, category name or ID.
    if q:
        search_filter = (
            Q(name__icontains=q)
            | Q(description__icontains=q)
            | Q(category__name__icontains=q)
        )

        # Allow searching by numeric product ID.
        if q.isdigit():
            search_filter |= Q(id=int(q))

        products = products.filter(search_filter)

    # Filter by category.
    active_category = None

    if category_id:
        if category_id.isdigit():
            active_category = Category.objects.filter(id=int(category_id)).first()

            if active_category:
                products = products.filter(category_id=active_category.id)
            else:
                category_id = ""
        else:
            category_id = ""

    # Filter by stock level.
    if stock == "in":
        products = products.filter(stock__gt=500)

    elif stock == "low":
        products = products.filter(stock__gt=0, stock__lte=500)

    elif stock == "out":
        products = products.filter(stock__lte=0)

    # Sort the filtered results.
    sort_options = {
        "newest": "-id",
        "name": "name",
        "price_asc": "price",
        "price_desc": "-price",
        "stock_asc": "stock",
    }

    if sort not in sort_options:
        sort = "newest"

    products = products.order_by(sort_options[sort], "id")

    # Paginate after filtering and sorting.
    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    # Preserve active filters in pagination links.
    query_params = request.GET.copy()
    query_params.pop("page", None)
    querystring = query_params.urlencode()

    return render(
        request,
        "see_product.html",
        {
            "products": page,
            "q": q,
            "category_id": category_id,
            "active_category": active_category,
            "stock": stock,
            "sort": sort,
            "categories": Category.objects.all().order_by("name"),
            "querystring": querystring,
        },
    )


# ============================================================
# EDIT PRODUCT
# ============================================================


@staff_member_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    # Remember the page that opened the edit form
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()
            cache.clear()

            if next_url:
                return redirect(next_url)

            return redirect("see_product")
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "add_product.html",
        {
            "form": form,
            "next_url": next_url,
        },
    )


@staff_member_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        product.delete()
        cache.clear()

        if next_url:
            return redirect(next_url)

        return redirect("see_product")

    return render(
        request,
        "delete_product.html",
        {
            "product": product,
            "next_url": next_url,
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


def product_review(request, id=None, product_id=None):
    product_id = product_id if product_id is not None else id

    product = get_object_or_404(Product, pk=product_id)

    # Display only approved reviews.
    feedbacks = (
        product.feedbacks.filter(is_approved=True)
        .select_related("user")
        .order_by("-created_at")
    )

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        form = FeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.product = product
            feedback.user = request.user

            # Reviews must be approved before public display.
            feedback.is_approved = True
            feedback.save()

            # messages.success(
            #     request,
            #     "Thank you! Your review has been submitted for approval.",
            # )

            return redirect(request.path)

    else:
        form = FeedbackForm()

    # Calculate the average using approved reviews only.
    rating_summary = feedbacks.aggregate(
        average_rating=Avg("rating"),
        total_reviews=Count("id"),
    )

    average_rating = rating_summary["average_rating"] or 0
    total_reviews = rating_summary["total_reviews"] or 0

    context = {
        "product": product,
        "feedbacks": feedbacks,
        "form": form,
        "average_rating": average_rating,
        "total_reviews": total_reviews,
    }

    return render(
        request,
        "feedback/product_feedback.html",
        context,
    )
