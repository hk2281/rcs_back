from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from rcs_back.utils.model import get_eco_emails


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
