from io import BytesIO
from random import Random

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw


CATEGORY_DATA = [
    {
        "name": "Букеты",
        "description": "Авторские композиции из свежих сезонных цветов.",
    },
    {
        "name": "Монобукеты",
        "description": "Минималистичные букеты из одного вида цветов.",
    },
    {
        "name": "Комнатные растения",
        "description": "Зелёные растения для дома, офиса и зимнего сада.",
    },
    {
        "name": "Подарочные наборы",
        "description": "Цветы с открытками, свечами и сладостями.",
    },
]

PRODUCER_DATA = [
    {
        "name": "Rose Atelier",
        "country": "Нидерланды",
        "description": "Поставщик премиальных роз и пионовидных сортов.",
    },
    {
        "name": "Green Habit",
        "country": "Беларусь",
        "description": "Локальная студия интерьерных растений и кашпо.",
    },
    {
        "name": "Flora Nord",
        "country": "Эквадор",
        "description": "Крупные поставки длинностебельных роз и гвоздик.",
    },
    {
        "name": "Botanic Mood",
        "country": "Италия",
        "description": "Декоративные сезонные композиции и лимитированные коллекции.",
    },
]

PRODUCT_TEMPLATES = [
    {
        "name": "Пудровое утро",
        "category": "Букеты",
        "price": "89.00",
        "stock": 12,
        "description": "Нежный букет из кустовых роз, эустомы и эвкалипта в молочно-розовой палитре.",
    },
    {
        "name": "Белые облака",
        "category": "Монобукеты",
        "price": "64.00",
        "stock": 8,
        "description": "Лаконичный монобукет из белых тюльпанов для утреннего сюрприза или спокойного интерьера.",
    },
    {
        "name": "Тропический ритм",
        "category": "Комнатные растения",
        "price": "120.00",
        "stock": 5,
        "description": "Крупная монстера деликатесная в декоративном кашпо для светлой гостиной.",
    },
    {
        "name": "Сад в коробке",
        "category": "Подарочные наборы",
        "price": "149.00",
        "stock": 6,
        "description": "Подарочная коробка с цветочной композицией, ароматической свечой и открыткой.",
    },
    {
        "name": "Вишнёвый закат",
        "category": "Букеты",
        "price": "97.00",
        "stock": 7,
        "description": "Эффектный букет из ранункулюсов, диантусов и бордовых роз с насыщенным характером.",
    },
    {
        "name": "Лавандовый воздух",
        "category": "Монобукеты",
        "price": "72.00",
        "stock": 10,
        "description": "Свежий монобукет из маттиолы и лаванды, который наполняет комнату мягким ароматом.",
    },
    {
        "name": "Оливковый уголок",
        "category": "Комнатные растения",
        "price": "138.00",
        "stock": 4,
        "description": "Оливковое дерево для тех, кто любит тёплые средиземноморские акценты в интерьере.",
    },
    {
        "name": "Тёплое письмо",
        "category": "Подарочные наборы",
        "price": "158.00",
        "stock": 3,
        "description": "Коробка с сезонными цветами, шоколадом ручной работы и мини-открыткой.",
    },
    {
        "name": "Рассветный пион",
        "category": "Букеты",
        "price": "115.00",
        "stock": 9,
        "description": "Пышный букет с пионовидными розами и лёгким садовым настроением.",
    },
    {
        "name": "Солнечный акцент",
        "category": "Монобукеты",
        "price": "58.00",
        "stock": 11,
        "description": "Яркие герберы в минималистичной упаковке для мгновенного хорошего настроения.",
    },
    {
        "name": "Фикус лирата",
        "category": "Комнатные растения",
        "price": "172.00",
        "stock": 2,
        "description": "Фактурное растение с крупными листьями для акцентной зоны в интерьере.",
    },
    {
        "name": "Комплимент дня",
        "category": "Подарочные наборы",
        "price": "84.00",
        "stock": 14,
        "description": "Небольшой цветочный набор с открыткой и сухоцветами для приятного жеста без повода.",
    },
]

PALETTES = [
    ("#f6d5dc", "#9d3f5d", "#fff4ef", "#4c744d"),
    ("#e1efd8", "#5e8a55", "#fff8ef", "#c27d5f"),
    ("#f8e3c2", "#d28f45", "#fffdf8", "#8b5f3d"),
    ("#ead9f2", "#8f5aa8", "#fff8ff", "#4f6d7a"),
]


def build_product_name(template, index):
    base_name = template["name"]
    if index < len(PRODUCT_TEMPLATES):
        return base_name
    return f"{base_name} #{index + 1}"


def create_mock_image_bytes(title, seed_value):
    random = Random(seed_value)
    width, height = 900, 700
    palette = PALETTES[seed_value % len(PALETTES)]

    image = Image.new("RGB", (width, height), palette[2])
    draw = ImageDraw.Draw(image)

    draw.ellipse((-120, -120, 340, 320), fill=palette[0])
    draw.ellipse((560, 60, 980, 480), fill=palette[1])
    draw.rectangle((0, height - 180, width, height), fill=palette[3])

    for _ in range(10):
        x = random.randint(80, width - 80)
        y = random.randint(120, height - 220)
        radius = random.randint(28, 48)
        petal_color = palette[random.randint(0, 2)]

        for dx, dy in ((0, -radius), (radius, 0), (0, radius), (-radius, 0)):
            draw.ellipse(
                (x + dx - radius, y + dy - radius, x + dx + radius, y + dy + radius),
                fill=petal_color,
            )
        draw.ellipse((x - 22, y - 22, x + 22, y + 22), fill="#fef7e8")

    draw.rounded_rectangle(
        (60, height - 145, width - 60, height - 55),
        radius=28,
        fill=(255, 255, 255),
    )
    draw.text((96, height - 122), title[:28], fill=palette[1])

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def build_mock_image_file(title, seed_value):
    filename = f"products/mock-product-{seed_value}.png"
    return filename, ContentFile(create_mock_image_bytes(title, seed_value))
