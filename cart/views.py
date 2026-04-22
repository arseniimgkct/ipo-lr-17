from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status

from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from ecom.serializers import CartSerializer

from catalog.models import Product

class CartViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related('product').all()

        if not items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        cart_data = []
        total_price = 0

        for item in items:
            item_total = float(item.product.price) * item.count

            cart_data.append({
                "product": item.product.name,
                "price": float(item.product.price),
                "count": item.count,
                "total": item_total
            })

            total_price += item_total

        from checkout.models import Checkout

        checkout = Checkout.objects.create(
            cart_items=cart_data,
            total_price=total_price
        )

        cart.items.all().delete()

        return Response({
            "status": "success",
            "checkout_id": checkout.id,
            "total_price": total_price
        }, status=status.HTTP_201_CREATED)
