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

    email = models.EmailField(
        verbose_name="email коменданта здания"
    )

    def current_mass(self) -> int:
        """Возвращает накопившуюся массу бумаги
        по зданию"""
        current_mass = 0
        for container in self.containers.all():
            if container.is_reported_enough():
                current_mass += container.capacity
        return current_mass

    def meets_mass_takeout_condition(self) -> bool:
        """Выполняются ли в корпусе условия для сбора.
        3 - условие на массу"""
        mass_condition = self.takeout_conditions.filter(
            type=3
        ).first()
        if mass_condition and self.current_mass() > mass_condition.number:
            return True
        else:
            return False

    def containers_for_takeout(self):
        """Возвращает список контейнеров, которые нужно вынести"""
        containers_for_takeout = []
        for container in self.containers.all():
            if container.needs_takeout():
                containers_for_takeout.append(container)
        return containers_for_takeout

    def needs_takeout(self) -> bool:
        """Нужно ли вынести бумагу?"""
        if self.meets_mass_takeout_condition():
            return True
        else:
            return False
        # Добавить условие на время

    def __str__(self) -> str:
        return self.address

    class Meta:
        verbose_name = "здание"
        verbose_name_plural = "здания"


class BuildingPart(models.Model):
    """Модель корпуса здания"""

    num = models.PositiveSmallIntegerField(
        verbose_name="номер корпуса"
    )

    building = models.ForeignKey(
        to=Building,
        on_delete=models.CASCADE,
        related_name="building_parts",
        verbose_name="здание"
    )

    def current_mass(self) -> int:
        """Возвращает накопившуюся массу бумаги
        по корпусу"""
        current_mass = 0
        for container in self.containers.all():
            if container.is_reported_enough():
                current_mass += container.capacity
        return current_mass

    def meets_mass_takeout_condition(self) -> bool:
        """Выполняются ли в корпусе условия для сбора.
        3 - условие на массу"""
        mass_condition = self.takeout_conditions.filter(
            type=3
        ).first()
        if mass_condition and self.current_mass() > mass_condition.number:
            return True
        else:
            return False

    def needs_takeout(self) -> bool:
        """Нужно ли вынести бумагу?"""
        if self.meets_mass_takeout_condition():
            return True
        else:
            return False
        # Добавить условие на время

    def containers_for_takeout(self):
        """Возвращает список контейнеров, которые нужно вынести"""
        containers_for_takeout = []
        for container in self.containers.all():
            if container.needs_takeout():
                containers_for_takeout.append(container)
        return containers_for_takeout

    def __str__(self) -> str:
        return f"корпус {self.num}"

    class Meta:
        verbose_name = "корпус здания"
        verbose_name_plural = "корпусы зданий"


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

    WAITING = 1
    ACTIVE = 2
    INACTIVE = 3
    STATUS_CHOICES = (
        (WAITING, "ожидает подключения"),
        (ACTIVE, "активный"),
        (INACTIVE, "не активный")
    )

    building = models.ForeignKey(
        to=Building,
        on_delete=models.PROTECT,
        related_name="containers",
        verbose_name="здание"
    )

    building_part = models.ForeignKey(
        to=BuildingPart,
        on_delete=models.CASCADE,
        related_name="containers",
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

    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=ACTIVE,
        verbose_name="состояние"
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

    email = models.EmailField(
        verbose_name="почта (для связи)",
        blank=True
    )

    phone = models.CharField(
        max_length=24,
        verbose_name="номер телефона (для связи)",
        blank=True
    )

    def last_full_report(self):
        """Возвращает FullContainerReport
        для этого контейнера, который ещё не
        отметили как опустошённый (то есть последний
        незакрытый), либо None"""
        return FullContainerReport.objects.filter(
            container=self).filter(
                emptied_at__isnull=True
        ).first()

    def ignore_reports_count(self) -> int:
        """Возвращает количество сообщений о заполненности,
        которое нужно игнорировать, если контейнер в общественом месте"""
        if not self.is_public:
            return 0
        if self.building_part:
            """type=4 - условие на игнорирование сообщений.
            В приоритете правило для корпуса"""
            building_part_condition = self.building_part.takeout_conditions.filter(
                type=4).first()
            if building_part_condition:
                return building_part_condition.number
        building_condition = self.building.takeout_conditions.filter(
            type=4).first()
        if building_condition:
            return building_condition.number
        else:
            return 0

    def is_reported_enough(self) -> bool:
        """Достаточно ли сообщений о заполненности поступило.
        Количество учиытвается только для общественных контейнеров."""
        if self.last_full_report():
            if not self.is_public:
                return True
            ignore_count = self.ignore_reports_count()
            if self.last_full_report().count > ignore_count:
                return True
        else:
            return False

    def needs_takeout(self) -> bool:
        """Нужно ли вынести контейнер"""
        if self.is_reported_enough():
            return True
        # Условие на вынос по времени

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
