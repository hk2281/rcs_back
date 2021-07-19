from datetime import datetime
from django.db import models
from django.utils import timezone

from rcs_back.containers_app.models import Container, Building


tz = timezone.get_default_timezone()


class ContainersTakeoutRequest(models.Model):
    """Модель отчёта о выносе контейнеров из здания"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время создания"
    )

    containers = models.ManyToManyField(
        to=Container,
        related_name="takeout_requests",
        verbose_name="выбранные для выноса контейнеры"
    )

    confirmed_at = models.DateTimeField(
        verbose_name="время подтверждения",
        blank=True,
        null=True
    )

    emptied_containers = models.ManyToManyField(
        to=Container,
        related_name="takeout_confirmations",
        verbose_name="контейнеры подтверждённые пустыми"
    )

    worker_info = models.CharField(
        max_length=2048,
        verbose_name="информация о рабочем",
        blank=True
    )

    def building(self) -> Building:
        container = self.containers.first()
        if container:
            return container.building
        else:
            return "контейнеры не выбраны"

    def __str__(self) -> str:
        return (f"Запрос выноса контейнеров от "
                f"{self.created_at.astimezone(tz).strftime('%d.%m.%Y %H:%M')}")

    class Meta:
        verbose_name = "запрос выноса контейнеров"
        verbose_name_plural = "запросы выноса контейнеров"


class TankTakeoutRequest(models.Model):
    """Модель отчёта вывоза бака"""

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

    mass = models.PositiveSmallIntegerField(
        verbose_name="масса вывоза в кг"
    )

    confirmed_at = models.DateTimeField(
        verbose_name="время подтверждения",
        blank=True,
        null=True
    )

    confirmed_mass = models.PositiveSmallIntegerField(
        verbose_name="подтверждённая масса вывоза в кг",
        blank=True,
        null=True
    )

    def wait_time(self) -> str:
        """Время ожидания вывоза"""
        if self.confirmed_at:
            return str(self.confirmed_at - self.created_at)
        else:
            return "Ещё не вывезли"

    def fill_time(self) -> str:
        """Время заполнения бака"""
        requests = TankTakeoutRequest.objects.filter(
            building=self.building
        ).filter(
            created_at__lt=self.created_at
        ).order_by(
            "-created_at"
        )
        if requests and requests[0].confirmed_at:
            return str(self.created_at-requests[0].confirmed_at)
        else:
            return "Нельзя посчитать"

    def __str__(self) -> str:
        return (f"Запрос вывоза накопительного бака от "
                f"{self.created_at.astimezone(tz).strftime('%d.%m.%Y %H:%M')} "
                f"в {self.building}")

    class Meta:
        verbose_name = "запрос вывоза бака"
        verbose_name_plural = "запросы вывоза баков"
