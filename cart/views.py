from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from catalog.models import Product
from django.db.models import F


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
def add_to_cart(request, pk):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, pk=pk)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        if item.count < product.quantity_in_stock:
            item.count += 1
            item.save()
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
