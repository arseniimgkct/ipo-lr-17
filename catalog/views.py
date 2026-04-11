from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Producer, ProductCategory
from django.core.paginator import Paginator


def product_list(request):
    qs = Product.objects.select_related('category', 'producer').all()

    q = request.GET.get('q')
    category_id = request.GET.get('category')
    producer_id = request.GET.get('producer')

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    if category_id:
        try:
            category_id = int(category_id)
            qs = qs.filter(category_id=category_id)
        except ValueError:
            pass

    if producer_id:
        try:
            producer_id = int(producer_id)
            qs = qs.filter(producer_id=producer_id)
        except ValueError:
            pass

    categories = ProductCategory.objects.all()
    producers = Producer.objects.all()

    paginator = Paginator(qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
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
