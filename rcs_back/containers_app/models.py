from django.db import models
from django_lifecycle import LifecycleModel, hook, AFTER_UPDATE

from rcs_back.takeouts_app.models import FullContainersNotification
from rcs_back.takeouts_app.utils import notify_about_full


class Building(models.Model):
    """ Модель здания """

    address = models.CharField(
        max_length=2048,
        verbose_name="адрес"
    )

    def check_full_count(self) -> bool:
        """Проверяет, достаточно ли в здании полных контейнеров
        для выноса"""
        full_count = Container.objects.filter(
            is_active=True
        ).filter(
            is_full=True
        ).filter(
            building=self
        ).count()
        is_enough = full_count >= 1  # FIXME
        return is_enough

    def __str__(self) -> str:
        return self.address

    class Meta:
        verbose_name = "здание"
        verbose_name_plural = "здания"


class Container(LifecycleModel):
    """ Модель контейнера """

    building = models.ForeignKey(
        to=Building,
        on_delete=models.PROTECT,
        related_name="containers",
        verbose_name="здание"
    )

    building_part = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="корпус"
    )

    floor = models.PositiveSmallIntegerField(
        verbose_name="этаж"
    )

    location = models.CharField(
        max_length=1024,
        verbose_name="аудитория/описание"
    )

    is_full = models.BooleanField(
        default=False,
        verbose_name="заполнен"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="активен"
    )

    @hook(AFTER_UPDATE, when="is_full", was=False, is_now=True)
    def on_fill(self) -> None:
        """При заполнении контейнера нужно зафиксировать,
        когда это произошло"""
        FullContainerReport.objects.create(
            container=self
        )
        full_building = self.building.check_full_count()
        if full_building:
            notify_about_full()

    def __str__(self) -> str:
        return f"Контейнер №{self.pk}"

    class Meta:
        verbose_name = "контейнер"
        verbose_name_plural = "контейнеры"


class FullContainerReport(models.Model):
    """Модель, хранящая информацию о том, когда
    был заполнен контейнер"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="первый раз получено"
    )

    container = models.ForeignKey(
        to=Container,
        on_delete=models.CASCADE,
        related_name="full_reports",
        verbose_name="контейнер"
    )

    count = models.SmallIntegerField(
        default=1,
        verbose_name="количество сообщений"
    )

    notification = models.ForeignKey(
        to=FullContainersNotification,
        on_delete=models.PROTECT,
        related_name="containers",
        blank=True,
        null=True,
        verbose_name="оповещение о полных контейнерах"
    )

    def __str__(self) -> str:
        return f"Контейнер №{self.container.pk} заполнен, {self.created_at}"

    class Meta:
        verbose_name = "контейнер заполнен"
        verbose_name_plural = "контейнеры заполнены"
