import qrcode

from django.conf import settings
from PIL import Image, ImageDraw, ImageFont


def generate_qr(container_id: int) -> Image:
    url = f"https://placeholder.com/containers/{container_id}"
    qr = qrcode.QRCode(
        box_size=10,
        border=9
    )
    qr.add_data(url)
    qr.make()
    sticker = qr.make_image()
    return sticker


def add_container_id(container_id: int, sticker: Image) -> Image:
    img1 = ImageDraw.Draw(sticker)
    font_path = str(settings.APPS_DIR / "containers_app" /
                    "utils" / "Roboto-Regular.ttf")
    font = ImageFont.truetype(font_path, 60)
    coords = (100, 0)
    text = f"id: {container_id}"
    img1.text(coords, text, font=font)
    return sticker


def add_logo(sticker: Image) -> Image:
    img1 = ImageDraw.Draw(sticker)
    font_path = str(settings.APPS_DIR / "containers_app" /
                    "utils" / "Roboto-Regular.ttf")
    font = ImageFont.truetype(font_path, 50)
    coords = (100, 400)
    text = "rcs-itmo.ru"
    img1.text(coords, text, font=font)
    return sticker


def generate_sticker(container_id: int) -> Image:
    qr = generate_qr(container_id=container_id)
    sticker = add_logo(add_container_id(container_id=container_id, sticker=qr))
    return sticker
