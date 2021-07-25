from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from rcs_back.containers_app.views import (BuildingListView,
                                           PublicFeedbackView,
                                           BuildingPartView)
from rcs_back.takeouts_app.views import *


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    re_path(r"auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
    path("containers", include("rcs_back.containers_app.urls")),
    path("buildings", BuildingListView.as_view()),
    path("container-takeout-requests/<int:pk>",
         ContainersTakeoutConfirmationView.as_view()),
    path("tank-takeout-requests", TankTakeoutRequestListView.as_view()),
    path("tank-takeout-requests/<int:pk>",
         TankTakeoutConfirmationView.as_view()),
    path("container-takeout-requests", ContainersTakeoutListView.as_view()),
    path("public-feedback", PublicFeedbackView.as_view()),
    path("building-parts", BuildingPartView.as_view()),
    path("takeout-conditions", TakeoutConditionListView.as_view()),
    path("takeout-conditions/<int:pk>", TakeoutConditionDetailView.as_view()),
    path("takeout-conditions/type-options",
         TakeoutConditionTypeOptionsView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
