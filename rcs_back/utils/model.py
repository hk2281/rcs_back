from django.conf import settings
from django.contrib.auth import get_user_model
from typing import List


def get_eco_emails() -> List[str]:
    """Список email'ов экологов"""
    ecos = get_user_model().objects.filter(
        groups__name=settings.ECO_GROUP
    )
    emails = []
    for eco in ecos:
        emails.append(eco.email)
    return emails
