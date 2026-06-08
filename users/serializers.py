from rest_framework import serializers

from .models import DefaultUser, Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", required=False)
    role = serializers.CharField(source="user.role", read_only=True)
    role_display = serializers.CharField(source="user.role_display", read_only=True)
    is_admin_role = serializers.BooleanField(source="user.is_admin_role", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "username",
            "email",
            "role",
            "role_display",
            "is_admin_role",
            "full_name",
            "phone",
            "address",
            "delivery_city",
            "delivery_index",
        )
        read_only_fields = ("username", "role", "role_display", "is_admin_role")

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        email = user_data.get("email")
        if email:
            instance.user.email = email
            instance.user.save(update_fields=["email"])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class OrderItemSerializer(serializers.Serializer):
    product = serializers.CharField()
    price = serializers.FloatField()
    count = serializers.IntegerField()
    total = serializers.FloatField()


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    customer_name = serializers.CharField()
    customer_email = serializers.CharField()
    customer_phone = serializers.CharField()
    delivery_address = serializers.CharField()
    items = OrderItemSerializer(many=True, source="cart_items")
    items_count = serializers.SerializerMethodField()

    def get_items_count(self, obj) -> int:
        return sum(int(item.get("count", 0)) for item in (obj.cart_items or []))
