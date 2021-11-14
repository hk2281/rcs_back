from django.apps import AppConfig


class ContainersAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rcs_back.containers_app"
    verbose_name = "Контейнеры"

    def ready(self):
        # pylint: disable=import-outside-toplevel,unused-import
        from rcs_back.containers_app import signals
