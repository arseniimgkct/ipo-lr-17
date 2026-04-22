from decimal import Decimal

from django.db.models import Sum

from checkout.models import Checkout

from .models import Cart, CartItem


def get_user_cart(user):
    return Cart.objects.get_or_create(user=user)


def add_product_to_cart(cart, product, count):
    if product.quantity_in_stock == 0:
        raise ValueError("Товара нет в наличии.")

    count = max(1, count)
    cart_item, _ = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"count": 0},
    )
    cart_item.count = min(product.quantity_in_stock, cart_item.count + count)
    cart_item.save()
    return cart_item


def cart_items_count(cart):
    return cart.items.aggregate(total=Sum("count"))["total"] or 0


def build_checkout_payload(items):
    cart_data = []
    total_price = Decimal("0.00")

    for item in items:
        item_total = item.product.price * item.count
        cart_data.append(
            {
                "product": item.product.name,
                "price": float(item.product.price),
                "count": item.count,
                "total": float(item_total),
            }
        )
        total_price += item_total

    return cart_data, total_price


def create_checkout_from_items(items):
    cart_data, total_price = build_checkout_payload(items)
    checkout = Checkout.objects.create(
        cart_items=cart_data,
        total_price=total_price,
    )
    return checkout, total_price
