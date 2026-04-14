from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.db.models import Q
from .models import Product, ProductCategory, Producer
from ecom.serializers import ProductSerializer, CategorySerializer, ManufacturerSerializer


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.select_related('category', 'producer').all()

        q = self.request.query_params.get('q')
        category_id = self.request.query_params.get('category')
        producer_id = self.request.query_params.get('producer')

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

        if category_id:
            try:
                qs = qs.filter(category_id=int(category_id))
            except ValueError:
                pass

        if producer_id:
            try:
                qs = qs.filter(producer_id=int(producer_id))
            except ValueError:
                pass

        return qs


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer


class ProducerViewSet(ReadOnlyModelViewSet):
    queryset = Producer.objects.all()
    serializer_class = ManufacturerSerializer