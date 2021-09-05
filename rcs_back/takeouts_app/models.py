import datetime

from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from typing import Union

from rcs_back.containers_app.models import Container, Building, BuildingPart


tz = timezone.get_default_timezone()


class ContainersTakeoutRequest(models.Model):
    """Модель отчёта о сборе контейнеров из здания"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время создания"
    )

    building = models.ForeignKey(
        to=Building,
        on_delete=models.CASCADE,
        related_name="containers_takeout_requests",
        verbose_name="здание"
    )

    building_part = models.ForeignKey(
        to=BuildingPart,
        on_delete=models.CASCADE,
        related_name="containers_takeout_requests",
        blank=True,
        null=True,
        verbose_name="корпус"
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
        blank=True,
        related_name="takeout_confirmations",
        verbose_name="контейнеры подтверждённые пустыми"
    )

    worker_info = models.CharField(
        max_length=2048,
        verbose_name="информация о рабочем",
        blank=True
    )

    def mass(self) -> int:
        """Возвращает массу бумаги в подтверждённых контейнерах"""
        mass = 0
        if self.emptied_containers.all():
            for container in self.emptied_containers.all():
                mass += container.mass()
        return mass

    def unconfirmed_containers(self) -> QuerySet:
        """Контейнеры, которые добавили в сбор при создании,
        но они не были опустошены"""
        return self.containers.difference(self.emptied_containers.all())

    def emptied_containers_match(self) -> float:
        """Соответствие (действительно собранных контейнеров /
        число из списка на сбор)"""
        return self.emptied_containers.count() / self.containers.count()

    def __str__(self) -> str:
        return (f"Запрос сбора контейнеров от "
                f"{self.created_at.astimezone(tz).strftime('%d.%m.%Y %H:%M')}")

    class Meta:
        verbose_name = "запрос сбора контейнеров"
        verbose_name_plural = "запросы сбора контейнеров"


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

    def wait_time(self) -> Union[datetime.timedelta, None]:
        """Время ожидания вывоза"""
        if self.confirmed_at:
            return self.confirmed_at - self.created_at
        else:
            return None

    def fill_time(self) -> Union[datetime.timedelta, None]:
        """Время заполнения бака"""
        requests = TankTakeoutRequest.objects.filter(
            building=self.building
        ).filter(
            created_at__lt=self.created_at
        ).order_by(
            "-created_at"
        )
        if requests and requests[0].confirmed_at:
            return self.created_at-requests[0].confirmed_at
        else:
            return None

    def mass(self) -> int:
        """Рассчитанная масса вывоза как
        сумма масс выносов контейнеров"""
        previous_tank_takeouts = TankTakeoutRequest.objects.filter(
            building=self.building,
            created_at__lt=self.created_at
        ).order_by("-created_at")
        if previous_tank_takeouts and previous_tank_takeouts[0].confirmed_at:
            previous_datetime = previous_tank_takeouts[0].confirmed_at
        else:
            previous_datetime = self.created_at - datetime.timedelta(days=365)
        takeouts = ContainersTakeoutRequest.objects.filter(
            building=self.building
        ).filter(
            created_at__gt=previous_datetime
        ).filter(
            created_at__lt=self.created_at
        )
        mass = 0
        for takeout in takeouts:
            mass += takeout.mass()
        return mass

    def confirmed_mass_match(self) -> Union[float, None]:
        """Соответствие (рассчитанная масса / подтверждённую"""
        if self.confirmed_mass:
            return self.mass() / self.confirmed_mass
        else:
            return None

    def mass_difference(self) -> Union[int, None]:
        """Разность рассчитанной массы и подтверждённой"""
        if self.confirmed_mass:
            return self.mass() - self.confirmed_mass
        else:
            return None

    def __str__(self) -> str:
        return (f"Запрос вывоза накопительного бака от "
                f"{self.created_at.astimezone(tz).strftime('%d.%m.%Y %H:%M')} "
                f"в {self.building}")

    class Meta:
        verbose_name = "запрос вывоза бака"
        verbose_name_plural = "запросы вывоза баков"


class TankTakeoutCompany(models.Model):
    """Модель компании, ответственной за вывоз бака"""

    email = models.EmailField(
        verbose_name="email"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="активна"
    )

    def __str__(self) -> str:
        return self.email

    class Meta:
        verbose_name = "компания, вывоза бака"
        verbose_name_plural = "компании, вывоз бака"


class TakeoutCondition(models.Model):
    """Модель условия для сбора"""

    OFFICE_DAYS = 1
    PUBLIC_DAYS = 2
    MASS = 3
    IGNORE_REPORTS = 4

    TYPE_CHOICES = (
        (OFFICE_DAYS, "не больше N дней в офисе"),
        (PUBLIC_DAYS, "не больше N дней в общественном месте"),
        (MASS, "суммарная масса бумаги в корпусе не больше N кг"),
        (IGNORE_REPORTS, ("игнорировать первые N сообщений "
                          "о заполненности контейнера в общественном месте"))
    )

    type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES,
        verbose_name="тип условия"
    )

    number = models.PositiveIntegerField(
        verbose_name="N"
    )

    building = models.ForeignKey(
        to=Building,
        on_delete=models.CASCADE,
        related_name="takeout_conditions",
        verbose_name="здание"
    )

    building_part = models.ForeignKey(
        to=BuildingPart,
        on_delete=models.CASCADE,
        related_name="takeout_conditions",
        null=True,
        blank=True,
        verbose_name="корпус здания"
    )

    def __str__(self) -> str:
        string = (f"Условие {self.get_type_display()} "
                  f"в {self.building}")
        if self.building_part:
            string += ", "
            string += str(self.building_part)
        return string

    class Meta:
        verbose_name = "условие для сбора"
        verbose_name_plural = "условия для сбора"
        constraints = [
            models.UniqueConstraint(
                fields=["building_part", "type"],
                name="unique_condition_for_building"
            )
        ]


class MassTakeoutConditionCommit(models.Model):
    """Модель фиксации выполнения
    условия на вынос по массе"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время создания"
    )

    building = models.ForeignKey(
        to=Building,
        on_delete=models.CASCADE,
        related_name="mass_condition_commits",
        verbose_name="здание"
    )

    building_part = models.ForeignKey(
        to=BuildingPart,
        on_delete=models.CASCADE,
        related_name="mass_condition_commits",
        null=True,
        blank=True,
        verbose_name="корпус здания"
    )

    def __str__(self) -> str:
        return (f"{self.created_at.astimezone(tz).strftime('%d.%m.%Y %H:%M')}"
                f"в {self.building}")

    class Meta:
        verbose_name = "выполнено условие для сбора"
        verbose_name_plural = "выполнены условия для сбора"
