from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from rcs_back.containers_app.views import BuildingListView
from rcs_back.takeouts_app.views import *


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    re_path(r"auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
    path("containers/", include("rcs_back.containers_app.urls")),
    path("buildings", BuildingListView.as_view()),
    path("takeout-confirmations",
         ContainersTakeoutConfirmationListView.as_view()),
    path("tank-takeout-requests", TankTakeoutRequestListView.as_view()),
    path("takeout-requests", ContainersTakeoutListView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
