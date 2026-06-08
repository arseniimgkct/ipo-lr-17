from itertools import cycle

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from cart.models import Cart, CartItem
from catalog.mock_data import (
    CATEGORY_DATA,
    PRODUCER_DATA,
    PRODUCT_TEMPLATES,
    build_mock_image_file,
    build_product_name,
)
from catalog.models import Producer, Product, ProductCategory
from checkout.models import Checkout
from users.models import Profile, Role


class Command(BaseCommand):
    help = "Заполняет магазин моковыми категориями, производителями и товарами."

    def add_arguments(self, parser):
        parser.add_argument(
            "--products",
            type=int,
            default=18,
            help="Сколько моковых товаров создать.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить текущие данные магазина перед заполнением.",
        )
        parser.add_argument(
            "--with-demo-user",
            action="store_true",
            help="Создать тестового пользователя demo / demo12345.",
        )
        parser.add_argument(
            "--with-admin",
            action="store_true",
            help="Создать тестового администратора admin / admin12345.",
        )
        parser.add_argument(
            "--with-manager",
            action="store_true",
            help="Создать тестового менеджера manager / manager12345.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        products_limit = max(1, options["products"])

        if options["clear"]:
            self.stdout.write("Очистка существующих данных магазина...")
            CartItem.objects.all().delete()
            Cart.objects.all().delete()
            Checkout.objects.all().delete()
            for product in Product.objects.exclude(image=""):
                product.image.delete(save=False)
            Product.objects.all().delete()
            Producer.objects.all().delete()
            ProductCategory.objects.all().delete()

        categories = {
            item["name"]: ProductCategory.objects.update_or_create(
                name=item["name"],
                defaults={"description": item["description"]},
            )[0]
            for item in CATEGORY_DATA
        }
        producers = [
            Producer.objects.update_or_create(
                name=item["name"],
                defaults={
                    "country": item["country"],
                    "description": item["description"],
                },
            )[0]
            for item in PRODUCER_DATA
        ]

        producer_cycle = cycle(producers)
        created_total = 0

        for index in range(products_limit):
            template = PRODUCT_TEMPLATES[index % len(PRODUCT_TEMPLATES)]
            product_name = build_product_name(template, index)
            producer = next(producer_cycle)
            product, _ = Product.objects.update_or_create(
                name=product_name,
                defaults={
                    "description": template["description"],
                    "price": template["price"],
                    "quantity_in_stock": template["stock"] + (index % 4),
                    "category": categories[template["category"]],
                    "producer": producer,
                },
            )

            filename, image_file = build_mock_image_file(product_name, index)
            if product.image:
                product.image.delete(save=False)
            product.image.save(filename, image_file, save=False)
            product.save()
            created_total += 1

        if options["with_demo_user"]:
            self._create_user(
                username="demo",
                password="demo12345",
                email="demo@example.com",
                first_name="Demo",
                last_name="User",
                role=Role.CUSTOMER,
            )

        if options["with_admin"]:
            self._create_user(
                username="admin",
                password="admin12345",
                email="admin@example.com",
                first_name="Bloom",
                last_name="Admin",
                role=Role.ADMIN,
                is_staff=True,
                is_superuser=True,
            )

        if options["with_manager"]:
            self._create_user(
                username="manager",
                password="manager12345",
                email="manager@example.com",
                first_name="Bloom",
                last_name="Manager",
                role=Role.MANAGER,
                is_staff=True,
            )

        self.stdout.write(
            self.style.SUCCESS(f"Готово: создано или обновлено {created_total} товаров.")
        )
        self.stdout.write(
            "Команда для запуска: ./.venv/bin/python manage.py seed_shop --clear --products 18 --with-demo-user --with-admin --with-manager"
        )

    def _create_user(
        self,
        *,
        username,
        password,
        email,
        first_name,
        last_name,
        role,
        is_staff=False,
        is_superuser=False,
    ):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            },
        )
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.role = role
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(password)
        user.save()

        profile, _ = Profile.objects.get_or_create(user=user)
        profile.full_name = f"{first_name} {last_name}".strip()
        profile.save()

        label = "создан" if created else "обновлён"
        self.stdout.write(
            self.style.SUCCESS(
                f"Пользователь {label}: {username} / {password} (роль: {user.get_role_display()})"
            )
        )
