from django.shortcuts import get_object_or_404, render
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from ecom.serializers import (
    CategorySerializer,
    ManufacturerSerializer,
    ProductSerializer,
)

from .models import Producer, Product, ProductCategory
from .services import filter_products, get_catalog_context, get_homepage_context


class ReadOnlyOrAdmin(permissions.BasePermission):
    message = "Только администратор может изменять каталог."

    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or getattr(user, "is_admin_role", False)
            )
        )


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


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        return filter_products(self.request.query_params)


class CategoryViewSet(ModelViewSet):
    queryset = ProductCategory.objects.order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdmin]


class ProducerViewSet(ModelViewSet):
    queryset = Producer.objects.order_by("name")
    serializer_class = ManufacturerSerializer
    permission_classes = [ReadOnlyOrAdmin]
