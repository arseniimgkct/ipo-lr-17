from rest_framework import serializers
from catalog.models import Product, ProductCategory, Producer
from cart.models import Cart, CartItem


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)


class ManufacturerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    country = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField()
    image = serializers.ImageField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = serializers.IntegerField()

    category = CategorySerializer()
    producer = ManufacturerSerializer()

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        producer_data = validated_data.pop('producer')

        category, _ = ProductCategory.objects.get_or_create(**category_data)
        producer, _ = Producer.objects.get_or_create(**producer_data)

        product = Product.objects.create(
            category=category,
            producer=producer,
            **validated_data
        )
        return product

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', None)
        producer_data = validated_data.pop('producer', None)

        if category_data:
            category, _ = ProductCategory.objects.get_or_create(**category_data)
            instance.category = category

        if producer_data:
            producer, _ = Producer.objects.get_or_create(**producer_data)
            instance.producer = producer

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CartItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    product = ProductSerializer()
    count = serializers.IntegerField()
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        return obj.price()


class CartSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return obj.total_price()