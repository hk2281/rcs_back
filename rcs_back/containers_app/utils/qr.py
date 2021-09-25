import qrcode

from qrcode.image.styledpil import StyledPilImage
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont


def generate_qr_with_logo(container_id: int) -> Image:
    """Генерирует QR код с ссылкой на фронт на контейнер и с лого"""
    url = settings.DOMAIN + f"containers/{container_id}"  # FIXME
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15
    )
    qr.add_data(url)
    qr.make()
    sticker = qr.make_image(
        image_factory=StyledPilImage,
        embeded_image_path=str(
            settings.APPS_DIR / "containers_app" /
            "utils" / "logo.png"
        )
    )
    return sticker


def add_background(sticker: Image) -> Image:
    """Вставляет задний фон для стикера"""
    background = Image.open(
        settings.APPS_DIR / "containers_app" /
        "utils" / "background.png"
    )
    sticker_w, sticker_h = sticker.size
    bg_w, bg_h = background.size
    offset = ((bg_w - sticker_w) // 2, (bg_h - sticker_h) // 2 + 120)
    background.paste(sticker, offset)
    return background


def add_container_id(sticker: Image, container_id: int) -> Image:
    """Вставляет id контейнера в стикер"""
    draw = ImageDraw.Draw(sticker)
    font_path = str(settings.APPS_DIR / "containers_app" /
                    "utils" / "MullerBold.ttf")
    font = ImageFont.truetype(font_path, 110)
    coords = (437, 340)
    text = f"ID {container_id}"
    draw.text(coords, text, fill="white", font=font, anchor="ms")
    return sticker


def generate_sticker(container_id: int) -> Image:
    """Создаёт стикер для контейнера по ID"""
    qr = generate_qr_with_logo(container_id=container_id)
    sticker = add_container_id(add_background(qr), container_id)
    return sticker


def add_border_background(sticker: Image) -> Image:
    """Вставляет задний фон для стикера с рамкой
    (версия для печати)"""
    background = Image.open(
        settings.APPS_DIR / "containers_app" /
        "utils" / "background-border.png"
    )
    sticker_w, sticker_h = sticker.size
    bg_w, bg_h = background.size
    offset = ((bg_w - sticker_w) // 2, (bg_h - sticker_h) // 2 + 120)
    background.paste(sticker, offset)
    return background


def generate_sticker_for_print(container_id: int) -> Image:
    """Создаёт стикер для контейнера по ID.
    Версия для печати - с рамкой"""
    qr: Image = generate_qr_with_logo(container_id=container_id)
    sticker: Image = add_container_id(add_border_background(qr), container_id)
    return sticker


def save_stickers_for_print(start_id: int, count: int) -> None:
    """Создаёт стикеры с указанными ID и сохраняет их в PDF"""
    for i in range(start_id, start_id + count):
        sticker: Image = generate_sticker_for_print(i)
        sticker.save(f"sticker_{i}.pdf", "pdf", quality=100)
