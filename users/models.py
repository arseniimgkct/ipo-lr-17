from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class Role(models.TextChoices):
    CUSTOMER = "CUSTOMER", "Покупатель"
    MANAGER = "MANAGER", "Менеджер"
    ADMIN = "ADMIN", "Администратор"


class DefaultUser(AbstractUser):
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.CUSTOMER,
        verbose_name="Роль",
    )

    @property
    def is_admin_role(self) -> bool:
        return self.role == Role.ADMIN or self.is_superuser

    @property
    def is_manager_role(self) -> bool:
        return self.role == Role.MANAGER or self.is_admin_role

    @property
    def role_display(self) -> str:
        return dict(Role.choices).get(self.role, self.role)

    def role_badge_class(self) -> str:
        return {
            Role.ADMIN: "bg-danger",
            Role.MANAGER: "bg-warning text-dark",
            Role.CUSTOMER: "bg-secondary",
        }.get(self.role, "bg-secondary")

    def get_absolute_url(self) -> str:
        return reverse("personal_cabinet")


class Profile(models.Model):
    user = models.OneToOneField(
        DefaultUser,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    full_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="ФИО",
    )
    phone = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Телефон",
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Адрес доставки",
    )
    delivery_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Город доставки",
    )
    delivery_index = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Почтовый индекс",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self) -> str:
        return f"Профиль: {self.user.username}"


def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
