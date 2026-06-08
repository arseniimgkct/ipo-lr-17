from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
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


def build_receipt_message(checkout):
    lines = [
        f"Спасибо за заказ #{checkout.pk} в Bloom Boutique!",
        "",
        "Состав заказа:",
    ]
    for item in checkout.cart_items:
        lines.append(
            f"- {item['product']}: {item['count']} x {item['price']} BYN = {item['total']} BYN"
        )
    lines.extend(
        [
            "",
            f"Итого: {checkout.total_price} BYN",
            f"Получатель: {checkout.customer_name}",
            f"Телефон: {checkout.customer_phone}",
            f"Адрес доставки: {checkout.delivery_address}",
        ]
    )
    return "\n".join(lines)


def send_checkout_receipt(checkout):
    if not checkout.customer_email:
        return 0

    return send_mail(
        subject=f"Чек по заказу #{checkout.pk} — Bloom Boutique",
        message=build_receipt_message(checkout),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[checkout.customer_email],
        fail_silently=False,
    )


def _resolve_customer_data(user, fallback):
    profile = getattr(user, "profile", None)
    full_name = (
        (profile.full_name if profile and profile.full_name else "")
        or user.get_full_name()
        or user.username
    )
    email = user.email or ""
    phone = (profile.phone if profile else "") or ""
    address = (profile.address if profile else "") or ""

    return {
        "customer_name": full_name or fallback.get("name", ""),
        "customer_email": email or fallback.get("email", ""),
        "customer_phone": phone or fallback.get("phone", ""),
        "delivery_address": address or fallback.get("address", ""),
    }


def create_checkout_from_items(items, user=None, form_data=None):
    cart_data, total_price = build_checkout_payload(items)
    fallback = form_data or {}
    customer = _resolve_customer_data(user, fallback) if user is not None else {
        "customer_name": fallback.get("name", ""),
        "customer_email": fallback.get("email", ""),
        "customer_phone": fallback.get("phone", ""),
        "delivery_address": fallback.get("address", ""),
    }

    checkout = Checkout.objects.create(
        user=user if user is not None and user.is_authenticated else None,
        cart_items=cart_data,
        total_price=total_price,
        **customer,
    )
    send_checkout_receipt(checkout)
    return checkout, total_price
