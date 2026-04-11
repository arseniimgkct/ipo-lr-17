from .models import Cart


def cart_counter(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.items.aggregate(total=models.Sum('count'))[
                'total'] or 0
        except Cart.DoesNotExist:
            count = 0
    else:
        count = 0
    return {'cart_items_count': count}
