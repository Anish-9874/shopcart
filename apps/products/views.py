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



# @cache_page(60 * 15)   can also be done by this this method can Caches the entire HTTP response
def product_list(request):
    products = cache.get("products")        #instead of Product.objects.all() we did this to learn cache (Caches only the data you choose)

    if products is None:
        print("Loading from database...")       #just to know data is retrived from database or not
        products = list(Product.objects.all())  #
        cache.set("products", products, 300)    #cache.set set the cache, we can clear it by cache.clear(), or delete by cache.delete("products")
    return render(request, "product_list.html", {"products": products})


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



def category_list(request):
    categories = Product.CATEGORY_CHOICES
    return render(request, "categories.html", {"categories": categories})


def category(request, category_name):
    products = Product.objects.filter(category=category_name)
    return render(request, "category_details.html", {
        "products": products,
        "category_name": category_name,
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