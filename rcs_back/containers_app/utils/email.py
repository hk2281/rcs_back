from typing import List
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string


def get_eco_emails() -> List[str]:
    """Список email'ов экологов"""
    ecos = get_user_model().objects.filter(
        groups__name=settings.ECO_GROUP
    )
    emails = []
    for eco in ecos:
        emails.append(eco.email)
    return emails


def send_public_feedback(email: str, msg: str, container_id: int = 0) -> None:
    """Отправляет сообщение с обратной связью на почту экологу"""

    full_msg = render_to_string("public_feedback.html", {
        "container_id": container_id,
        "msg": msg,
        "email": email
    }
    )

    email = EmailMessage(
        "Обратная связь на сайте RCS",
        full_msg,
        "noreply@rcs-itmo.ru",
        get_eco_emails()
    )
    email.content_subtype = "html"
    email.send()
