from django.contrib import admin
from .models import ProductCategory, Product, Producer

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "country")
    search_fields = ("name", "country")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "quantity_in_stock", "category", "producer")
    list_filter = ("category", "producer")
    search_fields = ("name",)
