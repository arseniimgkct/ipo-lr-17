from django.contrib import admin

from .models import Checkout


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "customer_name",
        "customer_email",
        "total_price",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "customer_name",
        "customer_email",
        "customer_phone",
        "user__username",
    )
    readonly_fields = ("created_at",)
