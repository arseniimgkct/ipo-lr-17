from django.db import models

class Checkout(models.Model):
    cart_items = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now=True, auto_now_add=True)
    total_price = models.IntegerField()