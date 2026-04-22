from django.shortcuts import get_object_or_404, render
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from ecom.serializers import CategorySerializer, ManufacturerSerializer, ProductSerializer

from .models import Producer, Product, ProductCategory
from .services import filter_products, get_catalog_context, get_homepage_context


def home(request):
    return render(request, "shop/index.html", get_homepage_context())


def catalog(request):
    return render(request, "shop/catalog.html", get_catalog_context(request.GET))


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category", "producer"),
        pk=pk,
    )
    return render(request, "shop/product_detail.html", {"product": product})


class ProductViewSet(ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return filter_products(self.request.query_params)


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = ProductCategory.objects.order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProducerViewSet(ReadOnlyModelViewSet):
    queryset = Producer.objects.order_by("name")
    serializer_class = ManufacturerSerializer
    permission_classes = [AllowAny]
