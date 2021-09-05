from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from rcs_back.containers_app.models import Container


@receiver(post_save, sender=Container)
def check_container_state(sender, instance: Container,
                          created: bool, **kwargs) -> None:
    """Записываем время активации"""
    if instance.is_active() and not instance.activated_at:
        instance.activated_at = timezone.now()
        instance.save()
