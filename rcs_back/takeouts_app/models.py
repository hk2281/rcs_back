from django.db import models


class EnoughFullContainersNotification(models.Model):
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

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время создания"
    )

    def __str__(self) -> str:
        return f"Запрос выноса от {self.created_at}"

    class Meta:
        verbose_name = "вынос"
        verbose_name_plural = "выносы"
