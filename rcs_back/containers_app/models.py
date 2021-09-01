import datetime

from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from typing import Union


tz = timezone.get_default_timezone()


class BaseBuilding(models.Model):
    """Абстрактный класс для общих методов
    здания и корпуса"""

    def current_mass(self) -> int:
        """Возвращает накопившуюся массу бумаги
        по зданию/корпусу"""
        current_mass = 0
        for container in self.containers.all():
            if container.is_full():
                current_mass += container.mass()
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
        """Выполняются ли в здании/корпусе условия для сбора
        по времени."""
        for container in self.containers.all():
            if container.check_time_conditions():
                return True
        return False

    def needs_takeout(self) -> bool:
        """Нужно ли вынести бумагу?"""
        return (self.meets_mass_takeout_condition() or
                self.meets_time_takeout_condition())

    def containers_for_takeout(self) -> QuerySet:
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
            confirmed_at__isnull=False
        ).order_by(
            "-created_at"
        ).first()
        if latest_commit and latest_takeout_request:
            if latest_commit.created_at > latest_takeout_request.created_at:
                return True
        if not latest_takeout_request and latest_commit:
            return True
        return False

    def calculated_collected_mass(self) -> int:
        """Собранная масса макулатуры, посчитанная как среднее"""
        mass = 0
        for request in self.containers_takeout_requests.filter(
            confirmed_at__isnull=False
        ):
            mass += request.mass()
        return mass

    def container_count(self) -> int:
        """Кол-во активных контейнеров"""
        return self.containers.filter(status=Container.ACTIVE).count()

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

    itmo_worker_name = models.CharField(
        max_length=128,
        verbose_name="ФИО коменданта здания",
        blank=True
    )

    itmo_worker_phone = models.CharField(
        max_length=16,
        verbose_name="номер коменданта здания",
        blank=True
    )

    get_container_room = models.CharField(
        max_length=64,
        verbose_name="аудитория, в которой можно получить контейнер",
        blank=True
    )

    get_sticker_room = models.CharField(
        max_length=64,
        verbose_name="аудитория, в которой можно получить стикер",
        blank=True
    )

    def get_building(self) -> "Building":
        return self

    def confirmed_collected_mass(self) -> int:
        """Суммарная масса собранной макулатуры,
        подтверждённая после вывоза бака"""
        mass = 0
        for request in self.tank_takeout_requests.all():
            if request.confirmed_mass:
                mass += request.confirmed_mass
        return mass

    def avg_fill_speed(self) -> float:
        """Средняя скорость сбора макулатуры (кг/месяц)"""
        if self.tank_takeout_requests.order_by("created_at")[0].confirmed_mass:
            start_date = self.tank_takeout_requests.order_by("created_at")[
                0].confirmed_at
        month_count = (timezone.now().year - start_date.year) * \
            12 + (timezone.now().month - start_date.month)
        return self.confirmed_collected_mass() / month_count

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

    def get_building(self) -> Building:
        return self.building

    def __str__(self) -> str:
        return f"корпус {self.num}"

    class Meta:
        verbose_name = "корпус здания"
        verbose_name_plural = "корпусы зданий"


class Container(models.Model):
    """ Модель контейнера """

    """Варианты статуса"""
    WAITING = 1
    ACTIVE = 2
    INACTIVE = 3
    STATUS_CHOICES = (
        (WAITING, "ожидает подключения"),
        (ACTIVE, "активный"),
        (INACTIVE, "не активный")
    )

    """Варианты вида"""
    ECOBOX = 1
    PUBLIC_ECOBOX = 2
    OFFICE_BOX = 3
    KIND_CHOICES = (
        (ECOBOX, "экобокс"),
        (PUBLIC_ECOBOX, "экобокс в общественном месте"),
        (OFFICE_BOX, "коробка из-под бумаги")
    )

    """Масса вида"""
    ECOBOX_MASS = 10
    PUBLIC_ECOBOX_MASS = 15
    OFFICE_BOX_MASS = 20

    kind = models.PositiveSmallIntegerField(
        choices=KIND_CHOICES,
        verbose_name="вид контейнера"
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

    room = models.CharField(
        max_length=16,
        blank=True,
        verbose_name="аудитория"
    )

    description = models.CharField(
        max_length=1024,
        verbose_name="описание",
        blank=True
    )

    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES,
        default=ACTIVE,
        verbose_name="состояние"
    )

    sticker = models.ImageField(
        verbose_name="стикер",
        upload_to="stickers/",
        blank=True
    )

    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="время активации"
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

    _is_full = models.BooleanField(
        default=False,
        verbose_name="полный (для сортировки)"
    )

    avg_takeout_wait_time = models.DurationField(
        blank=True,
        null=True,
        verbose_name="среднее время ожидания выноса контейнера"
    )

    avg_fill_time = models.DurationField(
        blank=True,
        null=True,
        verbose_name="cреднее время заполнения контейнера"
    )

    def mass(self) -> int:
        """Возвращает массу контейнера по его виду"""
        mass_dict = {
            self.ECOBOX: self.ECOBOX_MASS,
            self.PUBLIC_ECOBOX: self.PUBLIC_ECOBOX_MASS,
            self.OFFICE_BOX: self.OFFICE_BOX_MASS
        }

        if self.kind in mass_dict:
            return mass_dict[self.kind]
        else:
            return 0

    def collected_mass(self) -> int:
        """Рассчитанная суммарная масса, собранная из этого контейнера"""
        takeout_count = self.full_reports.filter(
            emptied_at__isnull=False
        ).count()
        return takeout_count * self.mass()

    def is_active(self) -> bool:
        """Активен ли контейнер?"""
        return self.status == self.ACTIVE

    def is_public(self) -> bool:
        """Находится в общественном месте?"""
        return self.kind == self.PUBLIC_ECOBOX

    def last_full_report(self) -> Union["FullContainerReport", None]:
        """Возвращает самый новый и
        незакрытый FullContainerReport
        для этого контейнера"""
        report = self.full_reports.order_by(
            "-reported_full_at"
        ).first()
        if report and not report.emptied_at:
            return report
        else:
            return None

    def last_emptied_report(self) -> Union["FullContainerReport", None]:
        """Возвращает последний закрытый FullContainerReport
        для этого контейнера"""
        reports = self.full_reports.order_by(
            "-reported_full_at"
        )
        if reports:
            if reports[0].emptied_at:
                return reports[0]
            if len(reports) > 1 and reports[1].emptied_at:
                return reports[1]
        else:
            return None

    def empty_from(self) -> Union[datetime.datetime, None]:
        """Возвращает, с какого момента контейнер является пустым"""
        if not self.is_full():
            if self.last_emptied_report():
                return self.last_emptied_report().emptied_at
            else:
                return self.activated_at
        else:
            return None

    def ignore_reports_count(self) -> int:
        """Возвращает количество сообщений о заполненности,
        которое нужно игнорировать, если контейнер в общественом месте"""
        if not self.is_public():
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

    def is_full(self) -> bool:
        """Полный ли контейнер?
        Учитывается количество сообщений, которые надо игнорировать."""
        if self.is_active() and self.last_full_report():

            if not self.is_public():
                return True

            if self.last_full_report().by_staff:
                return True

            ignore_count = self.ignore_reports_count()
            return self.last_full_report().count > ignore_count

        else:
            return False

    def is_reported_just_enough(self) -> bool:
        """Ровно ли достаточно сообщений о заполненности поступило,
        чтобы считать контейнер полным?"""
        if self.is_active() and self.last_full_report():
            if not self.is_public():
                return self.last_full_report().count == 1
            ignore_count = self.ignore_reports_count()
            return self.last_full_report().count == ignore_count + 1
        else:
            return False

    def get_time_condition_days(self) -> int:
        """Возвращает максимальное кол-во дней, которое
        этот контейнер может быть заполнен по условию"""
        if self.is_public():
            if (self.building_part and
                    self.building_part.public_days_condition()):
                return self.building_part.public_days_condition()
            else:
                return self.building.public_days_condition()
        else:
            if (self.building_part and
                    self.building_part.office_days_condition()):
                return self.building_part.office_days_condition()
            else:
                return self.building.office_days_condition()

    def check_time_conditions(self) -> bool:
        '''Выполнены ли условия "не больше N дней"'''
        if self.is_active() and self.get_time_condition_days():

            if self.is_full():
                days_full = self.cur_takeout_wait_time().days
                return days_full > self.get_time_condition_days()
            else:
                return False
        else:
            """Если такого условия нет, то False"""
            return False

    def needs_takeout(self) -> bool:
        """Нужно ли вынести контейнер"""
        return self.is_full() or self.check_time_conditions()

    def get_mass_rule_trigger(self) -> Union[Building, BuildingPart, None]:
        """Проверяет, выполняется ли условие по массе, и если да,
        то возвращает, чьё это условие"""
        if (self.building_part and
                self.building_part.meets_mass_takeout_condition()):
            return self.building_part
        elif self.building.meets_mass_takeout_condition():
            return self.building
        return None

    def cur_fill_time(self) -> Union[datetime.timedelta, None]:
        """Текущее время заполнения контейнера.
        Если None - то уже заполнен (либо не активен)"""
        if self.is_active():
            if self.last_full_report():
                return None
            else:
                fill_time = timezone.now() - self.empty_from()
                return fill_time
        else:
            return None

    def cur_takeout_wait_time(self) -> Union[datetime.timedelta, None]:
        """Текущее время ожидания выноса контейнера"""
        if self.is_active() and self.last_full_report():
            wait_time = (timezone.now() -
                         self.last_full_report().reported_full_at)
            return wait_time
        else:
            return None

    def calc_avg_fill_time(self) -> Union[datetime.timedelta, None]:
        """Считает среднее время заполнения контейнера
        (точнее, среднее время до первого сообщения о заполненности)"""
        reports = self.full_reports.order_by("reported_full_at")
        if len(reports) > 1:
            sum_time = datetime.timedelta(seconds=0)
            count = 0
            for i in range(len(reports) - 1):
                if reports[i].emptied_at:
                    fill_time = reports[i+1].reported_full_at - \
                        reports[i].emptied_at
                    sum_time += fill_time
                    count += 1
            avg_fill_time = sum_time / count
            return avg_fill_time
        else:
            return None

    def calc_avg_takeout_wait_time(self) -> Union[datetime.timedelta, None]:
        """Считает среднее время ожидания выноса контейнера"""
        reports = self.full_reports.all()
        if not reports or (len(reports) == 1 and not reports[0].emptied_at):
            return None
        else:
            sum_time = datetime.timedelta(seconds=0)
            count = 0
            for report in reports:
                if report.takeout_wait_time():
                    sum_time += report.takeout_wait_time()
                    count += 1
            avg_takeout_wait_time = sum_time / count
            return avg_takeout_wait_time

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

    by_staff = models.BooleanField(
        default=False,
        verbose_name="сотрудником"
    )

    def takeout_wait_time(self) -> Union[datetime.timedelta, None]:
        """Возвращает время ожидания выноса"""
        if self.emptied_at:
            return self.emptied_at - self.reported_full_at
        else:
            return None

    def __str__(self) -> str:
        return (f"Контейнер №{self.container.pk} заполнен, "
                f"{self.reported_full_at.astimezone(tz).strftime('%d.%m.%Y %H:%M')}")

    class Meta:
        verbose_name = "контейнер заполнен"
        verbose_name_plural = "контейнеры заполнены"
