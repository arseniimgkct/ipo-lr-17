from django.core.paginator import Paginator
from django.db.models import Q

from .models import Producer, Product, ProductCategory


CATALOG_PAGE_SIZE = 9


def get_base_products_queryset():
    return Product.objects.select_related("category", "producer").order_by("-id")


def filter_products(params):
    products = get_base_products_queryset()

    search_query = (params.get("search") or params.get("q") or "").strip()
    category_id = (params.get("category") or "").strip()
    producer_id = (params.get("producer") or "").strip()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    if category_id.isdigit():
        products = products.filter(category_id=int(category_id))

    if producer_id.isdigit():
        products = products.filter(producer_id=int(producer_id))

    return products


def get_homepage_context():
    return {
        "products": get_base_products_queryset()[:6],
        "categories": ProductCategory.objects.order_by("name"),
    }


def get_catalog_context(params):
    products = filter_products(params)
    paginator = Paginator(products, CATALOG_PAGE_SIZE)
    page_obj = paginator.get_page(params.get("page"))

    filter_params = params.copy()
    filter_params.pop("page", None)

    return {
        "page_obj": page_obj,
        "categories": ProductCategory.objects.order_by("name"),
        "producers": Producer.objects.order_by("name"),
        "search_query": params.get("search", "").strip(),
        "selected_category": params.get("category", "").strip(),
        "selected_producer": params.get("producer", "").strip(),
        "query_string": filter_params.urlencode(),
    }
