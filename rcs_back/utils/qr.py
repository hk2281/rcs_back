import qrcode

from PIL import Image, ImageDraw, ImageFont


def generate_url(container_id: int) -> str:
    url = f"https://placeholder.com/containers/{container_id}"
    return url


def generate_qr(container_id: int) -> Image:
    url = generate_url(container_id=container_id)
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
    font = ImageFont.truetype("./Roboto-Regular.ttf", 60)
    coords = (100, 0)
    text = f"id: {container_id}"
    img1.text(coords, text, font=font)
    return sticker


def add_logo(sticker: Image) -> Image:
    img1 = ImageDraw.Draw(sticker)
    font = ImageFont.truetype("./Roboto-Regular.ttf", 50)
    coords = (100, 400)
    text = "rcs-itmo.ru"
    img1.text(coords, text, font=font)
    return sticker


def generate_sticker(container_id: int) -> Image:
    qr = generate_qr(container_id=container_id)
    sticker = add_logo(add_container_id(container_id=container_id, sticker=qr))
    return sticker
