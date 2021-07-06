from django.conf import settings
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # Django Admin
    path(settings.ADMIN_URL, admin.site.urls),
    path("containers/", include("rcs_back.containers_app.urls")),
    path("takeouts/", include("rcs_back.takeouts_app.urls"))
]
