from openpyxl import Workbook
from io import BytesIO
from decimal import Decimal
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from catalog.models import Product


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    total = 0
    for item in items:
        item.total_price = item.product.price * item.count
        total += item.total_price

    return render(request, "shop/cart.html", {"items": items, "total": total})


@login_required
def add_to_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, pk=product_id)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.count = item.count or 0
        if item.count < product.quantity_in_stock:
            item.count += 1
    else:
        item.count = 1

    item.save()
    return redirect("cart_view")


@login_required
def update_cart(request, item_id):
    cart = Cart.objects.get(user=request.user)
    item = get_object_or_404(CartItem, cart=cart, id=item_id)

    if request.method == "POST":
        try:
            count = int(request.POST.get("count", 1))
            if count > item.product.quantity_in_stock:
                count = item.product.quantity_in_stock
            elif count < 1:
                count = 1
            item.count = count
            item.save()
        except ValueError:
            pass

    return redirect("cart_view")


@login_required
def remove_from_cart(request, item_id):
    cart = Cart.objects.get(user=request.user)
    item = get_object_or_404(CartItem, cart=cart, id=item_id)
    item.delete()
    return redirect("cart_view")


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    if not items.exists():
        return redirect('cart_view')

    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        email_to = request.POST.get('email', request.user.email).strip()

        if not address:
            return render(request, 'shop/checkout.html', {'cart': cart, 'error': 'Введите адрес доставки'})
        if not email_to:
            return render(request, 'shop/checkout.html', {'cart': cart, 'error': 'Введите email для чека'})

        total = sum(item.price() for item in items)

        wb = Workbook()
        ws = wb.active
        ws.title = "Чек"
        ws.append(['Товар', 'Цена', 'Кол-во', 'Сумма'])
        for item in items:
            ws.append([item.product.name, float(item.product.price),
                      item.count, float(item.price())])
        ws.append(['', '', 'Итого', float(total)])

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        filename = 'cheque.xlsx'

        email = EmailMessage(
            subject='Чек вашего заказа',
            body=f'Спасибо за ваш заказ! Адрес доставки: {address}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_to]
        )
        email.attach(filename, output.read(
        ), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send(fail_silently=False)

        cart.items.all().delete()

        return redirect('product_list')

    return render(request, 'shop/checkout.html', {'cart': cart})
