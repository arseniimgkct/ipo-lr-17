from django.shortcuts import render
from catalog.models import Product, ProductCategory


def index(request):
    products = Product.objects.all()[:8]
    categories = ProductCategory.objects.all()

    context = {
        "products": products,
        "categories": categories,
    }

    return render(request, "shop/index.html", context)
