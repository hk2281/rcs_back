from django.db import models


class FullContainersNotification(models.Model):
    """Модель оповещения о достаточном кол-ве
    полных контейнеров"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время создания"
    )

    def __str__(self) -> str:
        return f"Оповещение от {self.created_at}"

    class Meta:
        verbose_name = "оповещение о полных контейнерах"
        verbose_name_plural = "оповещения о полных контейнерах"


class TakeoutRequest(models.Model):
    """Модель запроса выноса"""

    notification = models.OneToOneField(
        to=FullContainersNotification,
        on_delete=models.PROTECT,
        verbose_name="оповещение"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время создания"
    )

    def __str__(self) -> str:
        return f"Запрос выноса от {self.created_at}"

    class Meta:
        verbose_name = "вынос"
        verbose_name_plural = "выносы"
