from django.db import models
from users.models import DefaultUser
from catalog.models import Product
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class Cart(models.Model):
    user = models.OneToOneField(
        DefaultUser, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Корзина пользователя: {self.user}'

    def total_price(self):
        return sum(item.price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.product.name} ({self.count} шт.)'

    def clean(self):
        if self.count > self.product.quantity_in_stock:
            raise ValidationError(
                "Count can't be greater than quantity in stock")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def price(self):
        return self.product.price * self.count
