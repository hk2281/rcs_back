from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django_lifecycle import LifecycleModel, hook, AFTER_UPDATE

from rcs_back.takeouts_app.models import EnoughFullContainersNotification
from rcs_back.users_app.models import User


class Building(models.Model):
    """ Модель здания """

    address = models.CharField(
        max_length=2048,
        verbose_name="адрес"
    )

    is_full = models.BooleanField(
        default=False,
        verbose_name="нужно вынести бумагу"
    )

    enough_full_containers_count = models.PositiveSmallIntegerField(
        verbose_name="достаточное количество контейнеров для выноса"
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
        is_enough = full_count >= self.enough_full_containers_count
        return is_enough

    def generate_full_msg(self) -> str:
        full_containers = Container.objects.filter(
            is_active=True
        ).filter(
            is_full=True
        ).filter(
            building=self
        )
        msg = "Список полных контейнеров:\n\n"
        for container in full_containers:
            msg += (f"Контейнер №{container.pk}, "
                    f"расположение: {container.building}, ")
            if container.building_part:
                msg += f"корпус {container.building_part}, "
            msg += (f"этаж {container.floor}, "
                    f"{container.location}.\n")
        msg += ("\nЭто сообщение было автоматически сгенерировано "
                "сервисом RCS for IF.")
        return msg

    def handle_full(self) -> None:
        """Фиксирует то, что накопилось достаточно
        полных контейнеров и оповещает сотрудников."""
        EnoughFullContainersNotification.objects.create()
        msg = self.generate_full_msg()
        subject = ("[RCS for IF] В корпусу ИТМО по адресу "
                   f"{self.address} накопилось достаточно полных контейнеров "
                   "с бумагой для выноса.")
        recipients = User.objects.filter(
            models.Q(groups__name=settings.ECO_GROUP) |
            models.Q(groups__name=settings.HOZ_GROUP)
        )
        recipient_list = []
        for recipient in recipients:
            recipient_list.append(recipient.email)
        send_mail(
            subject=subject,
            message=msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list
        )

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
        """Если в здании достаточно полных контейнеров,
        сообщаем"""
        if not self.building.is_full:
            is_building_full = self.building.check_full_count()
            if is_building_full:
                self.building.is_full = True
                self.building.save()
                self.building.handle_full()

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

    def __str__(self) -> str:
        return f"Контейнер №{self.container.pk} заполнен, {self.created_at}"

    class Meta:
        verbose_name = "контейнер заполнен"
        verbose_name_plural = "контейнеры заполнены"
