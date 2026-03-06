from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from django.db.models import F

@login_required
def add_to_cart(req, pk):
    pass

@login_required
def update_cart(req, product_id):
    cart = Cart.objects.get(user=req.user)
    try :
        value = CartItem.objects.filter(cart=cart, product=product_id).update(count=F('count' + 1))
        return HttpResponse(f'Количество товара: {value}')
    except CartItem.DoesNotExist:
        return HttpResponse('Товар не найден')
    except:
        return HttpResponse('Внутренняя ошибка')

@login_required
def remove_from_cart(req, item_id):
    try:
        product = CartItem.objects.get(id=item_id)
        product.delete()
        return HttpResponse('Объект удален')
    except CartItem.DoesNotExist:
        return HttpResponse('Товар не найден')
    except:
        return HttpResponse('Внутренняя ошибка')

@login_required
def cart_view(req):
    cart_items = CartItem.objects.get(cart=req.user)
    return render(req, '/shop/cart.html', cart_items)