from django.conf import settings
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # Django Admin
    path(settings.ADMIN_URL, admin.site.urls),
]
