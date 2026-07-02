from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm
from .models import Product

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



def product_list(request):
    products = Product.objects.all()
    return render(request, "product_list.html", {"products": products})



def see_product(request):

    products = Product.objects.all()

    return render(request, "see_product.html", {
        "products": products
    })


def category(request, category_id):
    categories = Product.objects.filter(category_id=category_id)
    return render(request, "categories.html", {"categories": categories})


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