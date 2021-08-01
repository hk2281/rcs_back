from typing import List
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from rcs_back.containers_app.models import Container


def get_eco_emails() -> List[str]:
    """Список email'ов экологов"""
    ecos = get_user_model().objects.filter(
        groups__name=settings.ECO_GROUP
    )
    emails = []
    for eco in ecos:
        emails.append(eco.email)
    return emails


def get_public_container_add_msg(container: Container) -> str:
    """Формируем сообщение для отправки после добавления
    контейнера через главную страницу"""
    msg = ("Вы получили это сообщение, потому что зарегистрировали контейнер "
           f"в сервисе RCS.\n\nID вашего контейнера: {container.pk}.\n"
           f"Электронная версия стикера: {container.sticker.url}.\n\n"
           "Для того чтобы активировать контейнер, вам необходимо "
           "получить физический стикер и контейнер. ")
    return msg


def send_public_feedback(email: str, msg: str, container_id: int = 0) -> None:
    """Отправляет сообщение с обратной связью на почту экологу"""
    full_msg = "Посетитель сайта RCS оставил обратную связь"
    if container_id:
        full_msg += f" по поводу контейнера №{container_id}"
    full_msg += ". Оригинальный текст обращения:\n\n"
    full_msg += msg
    full_msg += "\n\nEmail, указанный пользователем:\n"
    full_msg += email
    send_mail(
        "Обратная связь на сайте RCS",
        full_msg,
        "noreply@rcs-itmo.ru",
        get_eco_emails()
    )
