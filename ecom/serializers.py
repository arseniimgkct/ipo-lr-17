from rest_framework import serializers

from cart.models import Cart, CartItem
from catalog.models import Producer, Product, ProductCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ("id", "name", "description")


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = ("id", "name", "country", "description")


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    producer = ManufacturerSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "image",
            "image_url",
            "price",
            "quantity_in_stock",
            "is_available",
            "category",
            "producer",
        )

    def get_image_url(self, obj):
        if not obj.image:
            return ""

        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_is_available(self, obj):
        return obj.quantity_in_stock > 0


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ("id", "product", "count", "total_price")

    def get_total_price(self, obj):
        return obj.price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("id", "user", "created_at", "items", "total_price")

    def get_total_price(self, obj):
        return obj.total_price()
