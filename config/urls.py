from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from rcs_back.containers_app.views import (BuildingListView,
                                           PublicFeedbackView,
                                           BuildingPartView,
                                           FullContainerReportView)
from rcs_back.takeouts_app.views import *
from rcs_back.users_app.views import *


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/stats", include("rcs_back.stats_app.urls")),
    path("api/auth/users/me/", RetrieveCurrentUserView.as_view()),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    path("api/containers", include("rcs_back.containers_app.urls")),
    path("api/buildings", BuildingListView.as_view()),
    path("api/container-takeout-requests/<int:pk>",
         ContainersTakeoutConfirmationView.as_view()),
    path("api/container-takeout-requests/<int:pk>/container-list",
         ContainersForTakeoutView.as_view()),
    path("api/tank-takeout-requests", TankTakeoutRequestListView.as_view()),
    path("api/tank-takeout-requests/<int:pk>",
         TankTakeoutConfirmationView.as_view()),
    path("api/container-takeout-requests",
         ContainersTakeoutListView.as_view()),
    path("api/public-feedback", PublicFeedbackView.as_view()),
    path("api/building-parts", BuildingPartView.as_view()),
    path("api/takeout-conditions", TakeoutConditionListView.as_view()),
    path("api/takeout-conditions/<int:pk>",
         TakeoutConditionDetailView.as_view()),
    path("api/full-container-reports", FullContainerReportView.as_view()),
    path("api/collected-mass", CollectedMassView.as_view())
]

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
