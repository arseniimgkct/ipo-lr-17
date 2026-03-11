from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from users.models import DefaultUser

# PRODUCT CATEGORY


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# PRODUCER
class Producer(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# PRODUCT


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='data/')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity_in_stock = models.PositiveIntegerField()
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


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
