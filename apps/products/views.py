from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm
from apps.feedback.forms import FeedbackForm

from .models import Product
from django.core.cache import cache
from django.views.decorators.cache import cache_page


# Create your views here.

def add_product(request):

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            return redirect('add_product')

    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})



def delete_product(request, id):
    product = Product.objects.get(id=id)

    if request.method == "POST":
        product.delete()
        return redirect('see_product')

    return render(request, "delete_product.html", {"product": product})






from django.db.models import Q

def product_list(request):
    q = request.GET.get("q", "").strip()

    cache_key = f"products_{q}"

    products = cache.get(cache_key)          #instead of Product.objects.all() we did this to learn cache (Caches only the data you choose)

    if products is None:
        print("Loading from database...")         #just to know data is retrived from database or not

        if q:
            products = list(Product.objects.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            ))
        else:
            products = list(Product.objects.all())

        cache.set(cache_key, products, 300)     #cache.set set the cache, we can clear it by cache.clear(), or delete by cache.delete("products")

    return render(request, "product_list.html", {
        "products": products
    })


@cache_page(60 * 15)     #load from cache after first load
def see_product(request):

    products = Product.objects.all()

    return render(request, "see_product.html", {
        "products": products
    })





def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()
            return redirect('see_product')
    else:
        form = ProductForm(instance=product)

    return render(request, 'add_product.html', {'form': form})



from .models import Category

def category_list(request):
    categories = Category.objects.all()

    return render(request, "categories.html", {
        "categories": categories
    })


from django.shortcuts import get_object_or_404

def category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)

    return render(request, "category_details.html", {
        "products": products,
        "category": category,
    })




def product_review(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        form = FeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.product = product
            feedback.user = request.user
            feedback.save()

            return redirect("product_review", id=product.id)

    else:
        form = FeedbackForm()

    feedbacks = product.feedbacks.all()

    return render(request, "feedback.html", {
        "product": product,
        "feedbacks": feedbacks,
        "form": form,
    })