from django.db import models

from rcs_back.containers_app.models import Container, Building


class ContainersTakeoutRequest(models.Model):
    """Модель запроса выноса контейнеров из здания"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время создания"
    )

    containers = models.ManyToManyField(
        to=Container,
        related_name="takeout_requests",
        verbose_name="выбранные для выноса контейнеры"
    )

    confirmed = models.BooleanField(
        verbose_name="подтверждён",
        default=False
    )

    def __str__(self) -> str:
        return f"Запрос выноса контейнеров от {self.created_at}"

    class Meta:
        verbose_name = "запрос выноса контейнеров"
        verbose_name_plural = "запросы выноса контейнеров"


class ContainersTakeoutConfirmation(models.Model):
    """Модель подтверждения выноса контейнера"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время создания"
    )

    building = models.ForeignKey(
        to=Building,
        on_delete=models.PROTECT,
        related_name="confirmations",
        verbose_name="здание"
    )

    containers = models.ManyToManyField(
        to=Container,
        related_name="takeout_confirmations",
        verbose_name="контейнеры подтверждённые пустыми"
    )

    worker_info = models.CharField(
        max_length=2048,
        verbose_name="информация о рабочем"
    )

    def __str__(self) -> str:
        return (f"Подтверждение выноса контейнеров от {self.created_at} "
                f"в {self.building}")

    class Meta:
        verbose_name = "подтверждение выноса контейнеров"
        verbose_name_plural = "подтверждения выносов контейнеров"


class TankTakeoutRequest(models.Model):
    """Модель запроса вывоза накопительного бака"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время создания"
    )

    building = models.ForeignKey(
        to=Building,
        on_delete=models.CASCADE,
        related_name="tank_takeout_requests",
        verbose_name="здание"
    )

    def __str__(self) -> str:
        return (f"Запрос вывоза накопительного бака от {self.created_at} "
                "в {self.building}")

    class Meta:
        verbose_name = "запрос вывоза бака"
        verbose_name_plural = "запросы вывоза баков"
