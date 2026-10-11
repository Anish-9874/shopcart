from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.products.models import Product

from .forms import FeedbackForm


def product_feedback(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    feedbacks = product.feedbacks.filter(is_approved=True).select_related("user")

    if request.method == "POST":
        if not request.user.is_authenticated:
            login_url = reverse("login")
            return redirect(f"{login_url}?next={request.path}")

        form = FeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.product = product
            feedback.user = request.user
            feedback.is_approved = False
            feedback.save()

            messages.success(
                request,
                "Thank you! Your review has been submitted for approval.",
            )

            return redirect(
                "product_feedback",
                product_id=product.id,
            )
    else:
        form = FeedbackForm()

    rating_summary = feedbacks.aggregate(
        average_rating=Avg("rating"),
        total_reviews=Count("id"),
    )

    context = {
        "product": product,
        "feedbacks": feedbacks,
        "form": form,
        "average_rating": rating_summary["average_rating"] or 0,
        "total_reviews": rating_summary["total_reviews"],
    }

    return render(
        request,
        "feedback/product_feedback.html",
        context,
    )
