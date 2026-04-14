from django.db import models

class Checkout(models.Model):
    cart_items = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)