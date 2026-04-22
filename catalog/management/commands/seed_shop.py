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
            self._create_demo_user()

        self.stdout.write(
            self.style.SUCCESS(f"Готово: создано или обновлено {created_total} товаров.")
        )
        self.stdout.write(
            "Команда для запуска: ./.venv/bin/python manage.py seed_shop --clear --products 18 --with-demo-user"
        )

    def _create_demo_user(self):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username="demo",
            defaults={
                "email": "demo@example.com",
                "first_name": "Demo",
                "last_name": "User",
            },
        )
        user.set_password("demo12345")
        user.save()

        label = "создан" if created else "обновлён"
        self.stdout.write(f"Демо-пользователь {label}: demo / demo12345")
