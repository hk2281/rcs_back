from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "rcs_back.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import rcs_back.users.signals  # noqa F401
        except ImportError:
            pass
