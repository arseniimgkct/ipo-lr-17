from django.core.validators import MinValueValidator
from django.db import models
from django.templatetags.static import static


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Producer(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='data/')
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity_in_stock = models.PositiveIntegerField()
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)

    @property
    def display_image_url(self):
        if not self.image:
            return ""

        image_name = self.image.name
        if image_name.startswith(("data/products/mock-product-", "products/mock-product-")):
            return static(f"images/{image_name}")
        return self.image.url

    def __str__(self):
        return self.name
