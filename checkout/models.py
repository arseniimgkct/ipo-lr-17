from django.conf import settings
from django.db import models


class Checkout(models.Model):
    STATUS_CHOICES = (
        ("NEW", "Новый"),
        ("PROCESSING", "В обработке"),
        ("DELIVERED", "Доставлен"),
        ("CANCELLED", "Отменён"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Покупатель",
    )
    cart_items = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    customer_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Имя получателя",
    )
    customer_email = models.EmailField(
        blank=True,
        verbose_name="Электронная почта",
    )
    customer_phone = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Телефон",
    )
    delivery_address = models.TextField(
        blank=True,
        verbose_name="Адрес доставки",
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default="NEW",
        verbose_name="Статус",
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self) -> str:
        return f"Заказ #{self.pk} — {self.total_price} BYN"
