from django.db import models
from django.core.cache import cache
from django.utils import timezone


tz = timezone.get_default_timezone()


class BaseBuilding(models.Model):
    """Абстрактный класс для общих методов
    здания и корпуса"""

    def current_mass(self) -> int:
        """Возвращает накопившуюся массу бумаги
        по зданию/корпусу"""
        current_mass = 0
        for container in self.containers.all():
            if container.is_reported_enough():
                current_mass += container.capacity
        return current_mass

    def meets_mass_takeout_condition(self) -> bool:
        """Выполняются ли в здании/корпусе условия для сбора по общей массе.
        3 - условие на массу"""
        mass_condition = self.takeout_conditions.filter(
            type=3
        ).first()
        if mass_condition and self.current_mass() > mass_condition.number:
            return True
        else:
            return False

    def meets_time_takeout_condition(self) -> bool:
        '''Выполняются ли в здании/корпусе условия для сбора
        по времени.'''
        for container in self.containers.all():
            if container.check_time_conditions():
                return True
        return False

    def needs_takeout(self) -> bool:
        """Нужно ли вынести бумагу?"""
        return (self.meets_mass_takeout_condition() or
                self.meets_time_takeout_condition())

    def containers_for_takeout(self):
        """Возвращает список контейнеров, которые нужно вынести"""
        containers_for_takeout = []
        for container in self.containers.all():
            if container.needs_takeout():
                containers_for_takeout.append(container)
        return containers_for_takeout

    def public_days_condition(self) -> int:
        """Возвращает кол-во дней, через которое
        нужно выносить бумагу в общественных местах"""
        condition = self.takeout_conditions.filter(
            type=2
        ).first()
        if condition:
            return condition.number
        else:
            return 0

    def office_days_condition(self) -> int:
        """Возвращает кол-во дней, через которое
        нужно выносить бумагу в офисе"""
        condition = self.takeout_conditions.filter(
            type=1
        ).first()
        if condition:
            return condition.number
        else:
            return 0

    def is_mass_condition_commited(self) -> bool:
        """Зафиксировано ли выполнение условия по массе?"""
        latest_commit = self.mass_condition_commits.order_by(
            "-created_at"
        ).first()
        latest_takeout_request = self.containers_takeout_requests.filter(
            emptied_at__isnull=False
        ).order_by(
            "-created_at"
        ).first()
        if latest_commit and latest_takeout_request:
            if latest_commit.created_at > latest_takeout_request.created_at:
                return False
        return False

    class Meta:
        abstract = True


class Building(BaseBuilding):
    """ Модель здания """

    address = models.CharField(
        max_length=2048,
        verbose_name="адрес"
    )

    itmo_worker_email = models.EmailField(
        verbose_name="email коменданта здания",
        blank=True
    )

    containers_takeout_email = models.EmailField(
        verbose_name="email компании, выносящей баки",
        blank=True
    )

    def __str__(self) -> str:
        return self.address

    class Meta:
        verbose_name = "здание"
        verbose_name_plural = "здания"


class BuildingPart(BaseBuilding):
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

    def __str__(self) -> str:
        return f"корпус {self.num}"

    class Meta:
        verbose_name = "корпус здания"
        verbose_name_plural = "корпусы зданий"


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

    def last_unconfirmed_report(self):
        """Возвращает FullContainerReport
        для этого контейнера, который ещё не
        отметили как опустошённый (то есть последний
        незакрытый), либо None.
        Этот FullContainerReport также должен быть
        последним (актуальным)"""
        report = FullContainerReport.objects.filter(
            container=self).order_by(
                "-reported_full_at"
        ).first()
        if not report.emptied_at:
            return report
        else:
            return None

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
        if self.last_unconfirmed_report():
            if not self.is_public:
                return True
            ignore_count = self.ignore_reports_count()
            return self.last_unconfirmed_report().count > ignore_count
        else:
            return False

    def is_reported_just_enough(self) -> bool:
        """Ровно ли достаточно сообщений о заполненности поступило,
        чтобы считать контейнер полным?"""
        if self.last_unconfirmed_report():
            if not self.is_public:
                return self.last_unconfirmed_report().count == 1
            ignore_count = self.ignore_reports_count()
            return self.last_unconfirmed_report().count == ignore_count + 1
        else:
            return False

    def check_time_conditions(self) -> bool:
        '''Выполнены ли условия "не больше N дней"'''
        if self.last_unconfirmed_report():
            return True
        previous_reports = self.full_reports.order_by("-emptied_at")
        if not previous_reports:
            return False

        days = (timezone.now() - previous_reports[0].emptied_at).days
        if self.is_public:
            if (self.building_part.public_days_condition() and
                    days > self.building_part.public_days_condition()):
                return True
            if (self.building.public_days_condition() and
                    days > self.building.public_days_condition()):
                return True
            return False
        else:
            if (self.building_part.office_days_condition() and
                    days > self.building_part.office_days_condition()):
                return True
            if (self.building.office_days_condition() and
                    days > self.building.office_days_condition()):
                return True
            return False

    def needs_takeout(self) -> bool:
        """Нужно ли вынести контейнер"""
        return self.is_reported_enough() or self.check_time_conditions()

    def what_triggers_mass_rule(self):
        """Проверяет, выполняется ли правило по массе.
        Если да, то возвращает корпус контейнера или здание контейнера.
        Если нет, то возвращает None"""
        if (self.building_part and
                self.building_part.meets_mass_takeout_condition()):
            return self.building_part
        elif self.building.meets_mass_takeout_condition():
            return self.building
        return None

    def cur_fill_time(self) -> str:
        """Текущее время заполнения контейнера"""
        if self.last_unconfirmed_report():
            return "Контейнер уже заполнен."
        else:
            previous_reports = self.full_reports.order_by("-emptied_at")
            if previous_reports:
                fill_time = timezone.now() - previous_reports[0].emptied_at
                return str(fill_time)
            else:
                return "Пока нет информации о времени заполнения"

    def cur_takeout_wait_time(self) -> str:
        """Текущее время ожидания выноса контейнера"""
        if self.last_unconfirmed_report():
            wait_time = (timezone.now() -
                         self.last_unconfirmed_report().reported_full_at)
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
