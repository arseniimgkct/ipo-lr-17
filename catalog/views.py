from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Producer, ProductCategory


def product_list(request):
    qs = Product.objects.select_related('category', 'producer').all()

    q = request.GET.get('q')
    category_id = request.GET.get('category')
    producer_id = request.GET.get('producer')

    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )

    if category_id:
        qs = qs.filter(category_id=category_id)

    if producer_id:
        qs = qs.filter(producer_id=producer_id)

    categories = ProductCategory.objects.all()
    producers = Producer.objects.all()

    context = {
        'products': qs,
        'categories': categories,
        'producers': producers,
        'q': q,
        'selected_category': category_id,
        'selected_producer': producer_id,
    }
    return render(request, 'shop/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('category', 'producer'), pk=pk)
    context = {'product': product}
    return render(request, 'shop/product_detail.html', context)
