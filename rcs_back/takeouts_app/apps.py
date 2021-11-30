from django.apps import AppConfig


class TakeoutsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rcs_back.takeouts_app'
    verbose_name = "Сборы"

    def ready(self):
        # pylint: disable=import-outside-toplevel,unused-import
        from rcs_back.takeouts_app import signals
