# Цветочный магазин

## Структура проекта

- `catalog/` — модели товаров, категории, производители, HTML/API-вьюхи, сиды и management command.
- `cart/` — корзина, API корзины и сервисы для работы с заказом.
- `checkout/` — модель оформленного заказа.
- `users/` — регистрация и кастомный пользователь.
- `templates/` — общие шаблоны и переиспользуемые partials.
- `static/` — стили, JS и изображения интерфейса.
- `ecom/` — корневые настройки и маршрутизация Django-проекта.

## Где что искать

- Основная логика каталога: [catalog/services.py](/Users/arsenii/Learning/ipo/ipo-lr-17/catalog/services.py)
- Сидирование моковых данных: [catalog/management/commands/seed_shop.py](/Users/arsenii/Learning/ipo/ipo-lr-17/catalog/management/commands/seed_shop.py)
- Наборы моковых данных и генерация изображений: [catalog/mock_data.py](/Users/arsenii/Learning/ipo/ipo-lr-17/catalog/mock_data.py)
- Логика корзины: [cart/services.py](/Users/arsenii/Learning/ipo/ipo-lr-17/cart/services.py)
- Переиспользуемая карточка товара: [templates/includes/product_card.html](/Users/arsenii/Learning/ipo/ipo-lr-17/templates/includes/product_card.html)

## Заполнение базы

```bash
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py seed_shop --clear --products 18 --with-demo-user
```

После этого в базе появятся категории, производители, товары с моковыми изображениями и демо-пользователь:

- Логин: `demo`
- Пароль: `demo12345`
