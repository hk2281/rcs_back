from django.db import models
from django.core.cache import cache
from django.utils import timezone


tz = timezone.get_default_timezone()


class Building(models.Model):
    """ Модель здания """

    address = models.CharField(
        max_length=2048,
        verbose_name="адрес"
    )

    def __str__(self) -> str:
        return self.address

    class Meta:
        verbose_name = "здание"
        verbose_name_plural = "здания"


class TakeoutConditionMet(models.Model):
    """Модель оповещения о выполненных
    условиях для выноса"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время создания"
    )

    building = models.ForeignKey(
        to=Building,
        on_delete=models.CASCADE,
        related_name="full_containers_notifications",
        verbose_name="здание"
    )

    def __str__(self) -> str:
        return (f"Выполнено условие для выноса "
                f"{self.created_at.astimezone(tz).strftime('%d.%m.%Y %H:%M')}"
                f"в {self.building}")

    class Meta:
        verbose_name = "выполнено условие для выноса"
        verbose_name_plural = "выполнены условия для выноса"


class Container(models.Model):
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

    capacity = models.PositiveSmallIntegerField(
        verbose_name="объём"
    )

    is_full = models.BooleanField(
        default=False,
        verbose_name="заполнен"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="активен"
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name="находится в общественном месте"
    )

    sticker = models.ImageField(
        verbose_name="стикер",
        upload_to="stickers/",
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время добавления в систему"
    )

    def last_full_report(self):
        """Возвращает FullContainerReport
        для этого контейнера, который ещё не
        отметили как опустошённый"""
        return FullContainerReport.objects.filter(
            container=self).filter(
                emptied_at__isnull=True
        ).first()

    def cur_fill_time(self) -> str:
        """Текущее время заполнения контейнера"""
        if self.last_full_report():
            return "Контейнер уже заполнен."
        else:
            previous_reports = FullContainerReport.objects.filter(
                container=self).order_by("-emptied_at")
            if previous_reports:
                fill_time = timezone.now() - previous_reports[0].emptied_at
                return str(fill_time)
            else:
                return "Пока нет информации о времени заполнения"

    def cur_takeout_wait_time(self) -> str:
        """Текущее время ожидания выноса контейнера"""
        if self.last_full_report():
            wait_time = (timezone.now() -
                         self.last_full_report().reported_full_at)
            return str(wait_time)
        else:
            return "Контейнер ещё не заполнен."

    def avg_fill_time(self) -> str:
        """Среднее время заполнения этого контейнера"""
        avg_fill_time = cache.get(f"{self.pk}_avg_fill_time")
        if not avg_fill_time:
            return "Среднее время заполнения контейнера рассчитывается..."
        else:
            return avg_fill_time

    def avg_takeout_wait_time(self) -> str:
        """Среднее время ожидания выноса этого контейнера"""
        avg_takeout_wat_time = cache.get(f"{self.pk}_avg_takeout_wait_time")
        if not avg_takeout_wat_time:
            return "Среднее время ожидания выноса контейнера рассчитывается..."
        else:
            return avg_takeout_wat_time

    def __str__(self) -> str:
        return f"Контейнер №{self.pk}"

    class Meta:
        verbose_name = "контейнер"
        verbose_name_plural = "контейнеры"


class FullContainerReport(models.Model):
    """Модель, хранящая информацию о том, когда
    был заполнен и очищен контейнер"""

    reported_full_at = models.DateTimeField(
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

    emptied_at = models.DateTimeField(
        verbose_name="контейнер вынесен",
        blank=True,
        null=True
    )

    def __str__(self) -> str:
        return (f"Контейнер №{self.container.pk} заполнен, "
                f"{self.reported_full_at.astimezone(tz).strftime('%d.%m.%Y %H:%M')}")

    class Meta:
        verbose_name = "контейнер заполнен"
        verbose_name_plural = "контейнеры заполнены"
