from django.db import models


class Container(models.Model):
    """ Модель контейнера """

    is_full = models.BooleanField(
        default=False,
        verbose_name="заполнен"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="активен"
    )

    def __str__(self) -> str:
        return f"Контейнер №{self.pk}"

    class Meta:
        verbose_name = "контейнер"
        verbose_name_plural = "контейнеры"
