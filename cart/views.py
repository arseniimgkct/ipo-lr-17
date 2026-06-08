from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from catalog.models import Product
from ecom.serializers import CartSerializer

from .models import CartItem
from .services import (
    add_product_to_cart,
    cart_items_count,
    create_checkout_from_items,
    get_user_cart,
)


@login_required
def cart_view(request):
    cart, _ = get_user_cart(request.user)
    items = cart.items.select_related("product", "product__category", "product__producer")
    return render(
        request,
        "shop/cart.html",
        {
            "cart": cart,
            "items": items,
            "total": cart.total_price(),
        },
    )


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, _ = get_user_cart(request.user)

    try:
        count = int(request.POST.get("count", 1))
    except (TypeError, ValueError):
        count = 1

    try:
        add_product_to_cart(cart, product, count)
        messages.success(request, f"Товар «{product.name}» добавлен в корзину.")
    except ValueError as error:
        messages.error(request, str(error))

    redirect_to = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("cart_view")
    return HttpResponseRedirect(redirect_to)


@login_required
@require_POST
def update_cart(request, item_id):
    cart, _ = get_user_cart(request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    if item.product.quantity_in_stock == 0:
        item.delete()
        messages.info(request, "Товар закончился на складе и был удалён из корзины.")
        return redirect("cart_view")

    try:
        count = int(request.POST.get("count", item.count))
    except (TypeError, ValueError):
        count = item.count

    item.count = min(max(1, count), item.product.quantity_in_stock or 1)
    item.save()
    messages.success(request, "Количество товара обновлено.")
    return redirect("cart_view")


@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart, _ = get_user_cart(request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    messages.info(request, "Товар удалён из корзины.")
    return redirect("cart_view")


@login_required
def checkout_view(request):
    cart, _ = get_user_cart(request.user)
    items = cart.items.select_related("product")

    if request.method == "POST":
        if not items.exists():
            return render(
                request,
                "shop/checkout.html",
                {"cart": cart, "error": "Ваша корзина пуста."},
            )

        form_data = {
            "name": request.POST.get("name", ""),
            "email": request.POST.get("email", ""),
            "phone": request.POST.get("phone", ""),
            "address": request.POST.get("address", ""),
        }
        create_checkout_from_items(items, user=request.user, form_data=form_data)
        cart.items.all().delete()
        messages.success(request, "Заказ оформлен. Спасибо за покупку!")
        return redirect("personal_cabinet")

    return render(request, "shop/checkout.html", {"cart": cart})


class CartViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, _ = get_user_cart(request.user)
        return Response(CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def add(self, request):
        product_id = request.data.get("product_id") or request.data.get("product")

        try:
            product = Product.objects.get(pk=int(product_id))
        except (Product.DoesNotExist, TypeError, ValueError):
            return Response(
                {"error": "Товар не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            count = int(request.data.get("count", 1))
        except (TypeError, ValueError):
            count = 1

        cart, _ = get_user_cart(request.user)

        try:
            add_product_to_cart(cart, product, count)
        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "status": "success",
                "message": f"Товар «{product.name}» добавлен в корзину.",
                "cart_items_count": cart_items_count(cart),
                "cart": CartSerializer(cart, context={"request": request}).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        cart, _ = get_user_cart(request.user)
        items = cart.items.select_related("product").all()

        if not items.exists():
            return Response({"error": "Корзина пуста."}, status=status.HTTP_400_BAD_REQUEST)

        checkout, total_price = create_checkout_from_items(
            items,
            user=request.user,
            form_data=request.data,
        )
        cart.items.all().delete()

        return Response(
            {
                "status": "success",
                "checkout_id": checkout.id,
                "total_price": float(total_price),
            },
            status=status.HTTP_201_CREATED,
        )
