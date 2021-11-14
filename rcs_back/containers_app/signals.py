from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from rcs_back.containers_app.models import Building, BuildingPart, Container
from rcs_back.takeouts_app.models import TakeoutCondition


@receiver(post_save, sender=Container)
def check_container_state(instance: Container, **kwargs) -> None:
    """Записываем время активации"""
    if instance.is_active() and not instance.activated_at:
        instance.activated_at = timezone.now()
        instance.save()


@receiver(post_save, sender=Building)
def create_takeout_condition_for_building(instance: Building,
                                          created: bool, **kwargs) -> None:
    """Создаём условия для сбора при создании здания"""
    if created:
        TakeoutCondition.objects.create(
            building=instance
        )


@receiver(post_save, sender=BuildingPart)
def create_takeout_condition_for_bpart(instance: BuildingPart,
                                       created: bool, **kwargs) -> None:
    """Создаём условия для сбора при создании корпуса здания"""
    if created:
        TakeoutCondition.objects.create(
            building_part=instance
        )
