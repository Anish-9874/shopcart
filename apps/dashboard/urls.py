from django.contrib.auth.decorators import login_required
from django.urls import include, path

from apps.accounts import views as acc_views

from . import views

urlpatterns = [
    path("", include("apps.chat.urls")),
    path("login/", acc_views.login_view, name="login"),
    path("signup/", acc_views.signup_view, name="signup"),
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard",
    ),
    path(
        "admin-dashboard/reports/",
        views.reports_analytics,
        name="reports_analytics",
    ),
    path(
        "customer-dashboard/",
        views.customer_dashboard,
        name="customer_dashboard",
    ),
    path(
        "admin-reviews/",
        views.admin_reviews,
        name="admin_reviews",
    ),
    path(
        "admin-orders/",
        views.admin_orders,
        name="admin_orders",
    ),
    # Category Management
    path(
        "admin-categories/",
        views.admin_categories,
        name="admin_categories",
    ),
    path(
        "admin-categories/add/",
        views.admin_category_create,
        name="admin_category_create",
    ),
    path(
        "admin-categories/<int:category_id>/edit/",
        views.admin_category_edit,
        name="admin_category_edit",
    ),
    path(
        "admin-categories/<int:category_id>/delete/",
        views.admin_category_delete,
        name="admin_category_delete",
    ),
    path(
        "admin-categories/<int:category_id>/products/",
        views.admin_category_products,
        name="admin_category_products",
    ),
]
