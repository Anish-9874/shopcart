from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from apps.cart.models import Order, OrderItem
from apps.feedback.models import Feedback
from apps.notifications.services import send_notification
from apps.products.forms import CategoryForm
from apps.products.models import Category, Product

LOW_STOCK_LIMIT = 5


def _customer_queryset():
    # Exclude staff and superusers from customer statistics.
    return User.objects.filter(is_staff=False, is_superuser=False)


def _period_growth(current, previous):
    """Return percentage change, or None when no previous-period baseline exists."""
    if previous == 0:
        return None

    return round(((current - previous) / previous) * 100, 1)


@login_required
def customer_dashboard(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")

    featured_products = Product.objects.filter(is_featured=True).order_by("-id")[:8]

    categories = Category.objects.all().order_by("name")[:8]

    context = {
        "featured_products": featured_products,
        "categories": categories,
    }

    return render(request, "customer_dashboard.html", context)


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect("customer_dashboard")

    customers_count = _customer_queryset().count()

    orders_count = Order.objects.count()

    pending_orders_count = Order.objects.filter(status="Pending").count()

    products_count = Product.objects.count()

    low_stock_count = Product.objects.filter(stock__lte=LOW_STOCK_LIMIT).count()

    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:8]

    context = {
        "customers_count": customers_count,
        "orders_count": orders_count,
        "pending_orders_count": pending_orders_count,
        "products_count": products_count,
        "low_stock_count": low_stock_count,
        "recent_orders": recent_orders,
    }

    return render(request, "admin_dashboard.html", context)


@login_required
def reports_analytics(request):
    if not request.user.is_staff:
        return redirect("customer_dashboard")

    today = timezone.localdate()

    # Default to the last 30 days, including today.
    default_end = today
    default_start = today - timedelta(days=29)

    start = parse_date(request.GET.get("start", "")) or default_start
    end = parse_date(request.GET.get("end", "")) or default_end

    # Protect against an invalid date range.
    if start > end:
        start, end = end, start

    # Prevent unexpectedly large daily charts.
    if (end - start).days > 364:
        start = end - timedelta(days=364)

    period_days = (end - start).days + 1
    previous_end = start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=period_days - 1)

    period_orders = Order.objects.filter(created_at__date__range=(start, end))

    previous_orders = Order.objects.filter(
        created_at__date__range=(previous_start, previous_end)
    )

    # Cancelled orders do not count as sales.
    sales_orders = period_orders.exclude(status="Cancelled")
    previous_sales_orders = previous_orders.exclude(status="Cancelled")

    # Revenue means paid orders only.
    paid_orders = sales_orders.filter(payment_status=True)
    previous_paid_orders = previous_sales_orders.filter(payment_status=True)

    revenue = paid_orders.aggregate(total=Sum("total"))["total"] or 0

    previous_revenue = previous_paid_orders.aggregate(total=Sum("total"))["total"] or 0

    sales_value = sales_orders.aggregate(total=Sum("total"))["total"] or 0

    orders_count = sales_orders.count()
    previous_orders_count = previous_sales_orders.count()

    average_order_value = sales_value / orders_count if orders_count else 0

    revenue_growth = _period_growth(float(revenue), float(previous_revenue))

    orders_growth = _period_growth(orders_count, previous_orders_count)

    # Daily paid revenue chart.
    daily_revenue_rows = (
        paid_orders.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(value=Sum("total"))
        .order_by("day")
    )

    daily_revenue = {row["day"]: float(row["value"]) for row in daily_revenue_rows}

    # Daily non-cancelled order chart.
    daily_order_rows = (
        sales_orders.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(value=Count("id"))
        .order_by("day")
    )

    daily_orders = {row["day"]: row["value"] for row in daily_order_rows}

    # Daily customer registrations.
    customer_rows = (
        _customer_queryset()
        .filter(date_joined__date__range=(start, end))
        .annotate(day=TruncDate("date_joined"))
        .values("day")
        .annotate(value=Count("id"))
        .order_by("day")
    )

    daily_customers = {row["day"]: row["value"] for row in customer_rows}

    dates = [start + timedelta(days=offset) for offset in range(period_days)]

    revenue_chart = {
        "labels": [day.strftime("%d %b") for day in dates],
        "values": [daily_revenue.get(day, 0) for day in dates],
    }

    orders_chart = {
        "labels": [day.strftime("%d %b") for day in dates],
        "values": [daily_orders.get(day, 0) for day in dates],
    }

    customers_chart = {
        "labels": [day.strftime("%d %b") for day in dates],
        "values": [daily_customers.get(day, 0) for day in dates],
    }

    # Best-selling products during the selected period.
    item_value = ExpressionWrapper(
        F("price") * F("quantity"),
        output_field=DecimalField(
            max_digits=12,
            decimal_places=2,
        ),
    )

    top_products = (
        OrderItem.objects.filter(order__created_at__date__range=(start, end))
        .exclude(order__status="Cancelled")
        .values("product_name")
        .annotate(
            units_sold=Sum("quantity"),
            sales_value=Sum(item_value),
        )
        .order_by("-units_sold")[:8]
    )

    # Order status breakdown for the selected period.
    order_statuses = list(
        period_orders.values("status").annotate(total=Count("id")).order_by("status")
    )

    # Inventory alerts.
    low_stock_products = Product.objects.filter(stock__lte=LOW_STOCK_LIMIT).order_by(
        "stock", "name"
    )[:8]

    # Current overall customer and inventory totals.
    context = {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "customers_count": _customer_queryset().count(),
        "products_count": Product.objects.count(),
        "categories_count": Category.objects.count(),
        "orders_count": orders_count,
        "revenue": revenue,
        "sales_value": sales_value,
        "average_order_value": average_order_value,
        "revenue_growth": revenue_growth,
        "orders_growth": orders_growth,
        "paid_orders_count": paid_orders.count(),
        "unpaid_orders_count": sales_orders.filter(payment_status=False).count(),
        "cancelled_orders_count": period_orders.filter(status="Cancelled").count(),
        "top_products": top_products,
        "order_statuses": order_statuses,
        "low_stock_products": low_stock_products,
        "out_of_stock_count": Product.objects.filter(stock=0).count(),
        "revenue_chart": revenue_chart,
        "orders_chart": orders_chart,
        "customers_chart": customers_chart,
    }

    return render(request, "admin_reports.html", context)


@login_required
def admin_reviews(request):
    # Only staff members can access this page.
    if not request.user.is_staff:
        return redirect("customer_dashboard")

    reviews = Feedback.objects.select_related("user", "product").order_by("-created_at")

    # Search by reviewer, product, or review text.
    search_query = request.GET.get("q", "").strip()
    if search_query:
        reviews = reviews.filter(
            Q(user__username__icontains=search_query)
            | Q(product__name__icontains=search_query)
            | Q(message__icontains=search_query)
        )

    # Filter by star rating.
    rating = request.GET.get("rating", "")
    if rating in {"1", "2", "3", "4", "5"}:
        reviews = reviews.filter(rating=int(rating))

    # Delete a review only when the admin submits a POST request.
    if request.method == "POST":
        review_id = request.POST.get("review_id")
        review = get_object_or_404(Feedback, pk=review_id)
        review.delete()

        messages.success(request, "Review deleted successfully.")
        return redirect("admin_reviews")

    # Summary statistics.
    summary = Feedback.objects.aggregate(
        total=Count("id"),
        average=Avg("rating"),
    )

    context = {
        "reviews": reviews,
        "search_query": search_query,
        "selected_rating": rating,
        "total_reviews": summary["total"] or 0,
        "average_rating": summary["average"] or 0,
        "five_star_reviews": Feedback.objects.filter(rating=5).count(),
    }

    return render(request, "admin_reviews.html", context)


@login_required
def admin_orders(request):
    # Only staff members can manage orders.
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to manage orders.")
        return redirect("customer_dashboard")

    # Handle order updates.
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")
        payment_value = request.POST.get("payment_status")

        order = get_object_or_404(Order, pk=order_id)

        # Validate delivery status.
        valid_statuses = {value for value, label in Order.STATUS}

        if new_status not in valid_statuses:
            messages.error(request, "Invalid order status.")
            return redirect("admin_orders")

        # Validate payment status.
        if payment_value not in {"paid", "unpaid"}:
            messages.error(request, "Invalid payment status.")
            return redirect("admin_orders")

        # Prevent cancelled orders from being marked as paid.
        if new_status == "Cancelled" and payment_value == "paid":
            messages.error(request, "A cancelled order cannot be marked as paid here.")
            return redirect("admin_orders")

        # Store previous values before updating.
        old_status = order.status
        old_payment_status = order.payment_status

        # Update order.
        order.status = new_status
        order.payment_status = payment_value == "paid"

        order.save(
            update_fields=[
                "status",
                "payment_status",
                "updated_at",
            ]
        )

        # Send notification when delivery status changes.
        if old_status != order.status:
            send_notification(
                user=order.user,
                title="Order Status Updated",
                message=(
                    f"Your order #{order.id} status has changed "
                    f"from {old_status} to {order.status}."
                ),
                sender=request.user,
                order=order,
            )

        # Send notification when payment status changes.
        if old_payment_status != order.payment_status:
            payment_label = "Paid" if order.payment_status else "Unpaid"

            send_notification(
                user=order.user,
                title="Payment Status Updated",
                message=(
                    f"Payment for your order #{order.id} "
                    f"has been marked as {payment_label.lower()}."
                ),
                sender=request.user,
                order=order,
            )

        messages.success(request, f"Order #{order.id} updated successfully.")
        return redirect("admin_orders")

    # Display orders.
    orders = (
        Order.objects.select_related("user")
        .prefetch_related("items")
        .order_by("-created_at")
    )

    # Search and filters.
    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "")
    payment_filter = request.GET.get("payment", "")

    if search_query:
        orders = orders.filter(
            Q(full_name__icontains=search_query)
            | Q(phone__icontains=search_query)
            | Q(user__username__icontains=search_query)
            | Q(id__icontains=search_query)
        )

    if status_filter in {value for value, label in Order.STATUS}:
        orders = orders.filter(status=status_filter)

    if payment_filter == "paid":
        orders = orders.filter(payment_status=True)
    elif payment_filter == "unpaid":
        orders = orders.filter(payment_status=False)

    context = {
        "orders": orders,
        "search_query": search_query,
        "status_filter": status_filter,
        "payment_filter": payment_filter,
        "status_choices": Order.STATUS,
    }

    return render(
        request,
        "admin_orders.html",
        context,
    )


@login_required
def admin_categories(request):
    if not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect("customer_dashboard")

    categories = Category.objects.all().order_by("name")

    return render(
        request,
        "admin_categories.html",
        {"categories": categories},
    )


@login_required
def admin_category_create(request):
    if not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect("customer_dashboard")

    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Category created successfully.",
            )
            return redirect("admin_categories")
    else:
        form = CategoryForm()

    return render(
        request,
        "admin_category_form.html",
        {
            "form": form,
            "page_title": "Add Category",
        },
    )


@login_required
def admin_category_edit(request, category_id):
    if not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect("customer_dashboard")

    category = get_object_or_404(Category, pk=category_id)

    if request.method == "POST":
        form = CategoryForm(
            request.POST,
            request.FILES,
            instance=category,
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Category updated successfully.",
            )
            return redirect("admin_categories")
    else:
        form = CategoryForm(instance=category)

    return render(
        request,
        "admin_category_form.html",
        {
            "form": form,
            "page_title": "Edit Category",
            "category": category,
        },
    )


@login_required
def admin_category_delete(request, category_id):
    if not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect("customer_dashboard")

    category = get_object_or_404(Category, pk=category_id)

    if request.method == "POST":
        if category.products.exists():
            messages.error(
                request,
                "This category contains products. "
                "Move its products to another category first.",
            )
        else:
            if category.image:
                category.image.delete(save=False)

            category.delete()

            messages.success(
                request,
                "Category deleted successfully.",
            )

        return redirect("admin_categories")

    return render(
        request,
        "admin_category_confirm_delete.html",
        {"category": category},
    )


@login_required
def admin_category_products(request, category_id):
    if not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect("customer_dashboard")

    category = get_object_or_404(Category, pk=category_id)

    products = category.products.all().order_by("name")

    return render(
        request,
        "admin_category_products.html",
        {
            "category": category,
            "products": products,
        },
    )
