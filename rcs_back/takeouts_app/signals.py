import datetime

from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone

from rcs_back.takeouts_app.models import ContainersTakeoutRequest


@receiver(post_save)
def notify_about_archive(instance: ContainersTakeoutRequest, created: bool, **kwargs):
    if created and instance.archive_room:
        emails = instance.building.get_worker_emails()
        msg = render_to_string("archive_takeout.html", {
            "address": instance.building.address,
            "room": instance.archive_room,
            "email": instance.requesting_worker_email,
            "phone": instance.requesting_worker_phone,
            "description": instance.archive_description,
            "due_date": timezone.now().date() + datetime.timedelta(days=1)
        }
        )

        email = EmailMessage(
            "Оповещение от сервиса RecycleStarter",
            msg,
            None,
            emails
        )
        email.content_subtype = "html"
        email.send()
