from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from cart.models import Cart, CartItem
from catalog.models import Product
from .models import Checkout

@login_required
def checkout(req):
    cart = Cart.objects.all().filter(user=req.user)
    items = CartItem.objects.filter(cart=cart)
    
    total_price = 0
    for item in items:
        total_price += item.product.price
    
    
    
    checkout = Checkout(cart_items=items, total_price=total_price)
    
    checkout.save()
    
    return