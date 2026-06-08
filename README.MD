# Цветочный магазин

## Структура проекта

- `catalog/` — модели товаров, категории, производители, HTML/API-вьюхи, сиды и management command.
- `cart/` — корзина, API корзины и сервисы для работы с заказом.
- `checkout/` — модель оформленного заказа (привязана к пользователю).
- `users/` — регистрация, профиль, личный кабинет, API `/api/me/` и `/api/orders/`.
- `templates/` — общие шаблоны, личный кабинет, настройки.
- `static/` — стили, JS и изображения интерфейса.
- `ecom/` — корневые настройки и маршрутизация Django-проекта.

## Где что искать

- Основная логика каталога: [catalog/services.py](/Users/arsenii/Learning/ipo/ipo-lr-17/catalog/services.py)
- Сидирование моковых данных: [catalog/management/commands/seed_shop.py](/Users/arsenii/Learning/ipo/ipo-lr-17/catalog/management/commands/seed_shop.py)
- Наборы моковых данных и генерация изображений: [catalog/mock_data.py](/Users/arsenii/Learning/ipo/ipo-lr-17/catalog/mock_data.py)
- Логика корзины: [cart/services.py](/Users/arsenii/Learning/ipo/ipo-lr-17/cart/services.py)
- Переиспользуемая карточка товара: [templates/includes/product_card.html](/Users/arsenii/Learning/ipo/ipo-lr-17/templates/includes/product_card.html)
- Модели пользователя/профиля: [users/models.py](/Users/arsenii/Learning/ipo/ipo-lr-17/users/models.py)
- API профиля и заказов: [users/views.py](/Users/arsenii/Learning/ipo/ipo-lr-17/users/views.py)

## Авторизация и роли

Используется **гибридная** авторизация:

- **Session auth** для веб-интерфейса (`/accounts/login/`, `/accounts/signup/`, `/accounts/logout/`).
- **Token auth** для API (`/api-token-auth/`). Токен передаётся в `Authorization: Token <key>` или в `Authorization: Bearer <key>`.

Роли пользователей (`users.models.Role`):

- `CUSTOMER` — покупатель (по умолчанию).
- `MANAGER` — менеджер.
- `ADMIN` — администратор.

Дополнительные свойства `User`:

- `is_admin_role` — `True` для админа/суперюзера.
- `is_manager_role` — `True` для менеджера и админа.
- `role_display` — локализованное имя роли.
- `role_badge_class()` — Bootstrap-класс для бейджа.

## Основные URL

- `GET /` — главная
- `GET /catalog/` — каталог
- `GET /catalog/<id>/` — карточка товара
- `GET /cart/` — корзина
- `POST /cart/add/<id>/` — добавить товар
- `POST /cart/checkout/` — оформить заказ
- `GET /accounts/signup/` — регистрация
- `GET /accounts/login/` — вход
- `POST /accounts/logout/` — выход
- `GET /accounts/account/` — личный кабинет
- `GET /accounts/account/settings/` — настройки (смена профиля и пароля)
- `GET /accounts/account/orders/<id>/` — детали заказа

## API

- `GET /api/me/` — профиль текущего пользователя (требует авторизации).
- `PATCH /api/me/` — частичное обновление профиля.
- `GET /api/orders/` — список заказов (покупатель видит только свои, админ — все).
- `GET /api/orders/<id>/` — детали заказа (с проверкой прав).
- `GET /api/products/` — каталог (доступен всем).
- `POST/PUT/PATCH/DELETE /api/products/` — только админу.
- `GET /api/categories/`, `/api/producers/` — доступны всем; запись — только админу.
- `POST /api-token-auth/` — получение токена по `username`/`password`.

## Заполнение базы

```bash
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py seed_shop --clear --products 18 \
  --with-demo-user --with-admin --with-manager
```

После этого в базе появятся категории, производители, товары с моковыми изображениями и три тестовых аккаунта:

| Логин    | Пароль         | Роль          |
|----------|----------------|---------------|
| `demo`   | `demo12345`    | Покупатель    |
| `manager`| `manager12345` | Менеджер      |
| `admin`  | `admin12345`   | Администратор |

## Права доступа

| Действие                                    | Гость | Покупатель | Менеджер | Админ |
|---------------------------------------------|:-----:|:----------:|:--------:|:-----:|
| Каталог `GET /api/products/`                |  ✓   |     ✓     |    ✓    |  ✓   |
| Создание/изменение товара                   |  401 |    403    |   403   |  ✓   |
| `GET /api/me/`                              |  401 |    200    |   200   |  200  |
| `PATCH /api/me/`                            |  401 |    200    |   200   |  200  |
| `GET /api/orders/` (свои / все)             |  401 |  только свои | только свои | все |
| `/accounts/account/`                        |  → login | ✓   |    ✓    |   ✓   |

## Поля профиля

Помимо стандартного `User` (`username`, `email`, `role`), в `users.models.Profile`:

- `full_name` — ФИО.
- `phone` — телефон.
- `address` — адрес доставки.
- **`delivery_city`** — город доставки (специфика магазина).
- **`delivery_index`** — почтовый индекс (специфика магазина).
