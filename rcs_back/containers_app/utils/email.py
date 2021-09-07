from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

from rcs_back.containers_app.models import Container, EmailToken
from rcs_back.utils.model import building_worker_emails, get_eco_emails


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


def container_activation_request_notify(container: Container,
                                        token: EmailToken) -> None:
    """Отправляет запрос на активацию экологу и коменданту здания"""

    emails = building_worker_emails(container.building)
    if emails:
        activation_link = settings.DOMAIN + "/api/containers/"  # FIXME
        activation_link += str(container.pk)
        activation_link += f"/activate?token={token.token}"
        msg = render_to_string("container_activation_request.html", {
            "container": container,
            "activation_link": activation_link
        }
        )

        email = EmailMessage(
            "Запрос активации контейнера на сайте RCS",
            msg,
            "noreply@rcs-itmo.ru",
            emails
        )
        email.content_subtype = "html"
        email.send()
