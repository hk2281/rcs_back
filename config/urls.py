from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from rcs_back.containers_app.views import BuildingListView


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("containers/", include("rcs_back.containers_app.urls")),
    path("takeouts/", include("rcs_back.takeouts_app.urls")),
    re_path(r"auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
    path("buildings/", BuildingListView.as_view())
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
