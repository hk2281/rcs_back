from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from rcs_back.containers_app.views import (
    BuildingListView,
    BuildingPartView,
    ContainerCountView,
    FullContainerReportView,
    PublicFeedbackView,
)
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
         ContainersTakeoutDetailView.as_view()),
    path("api/container-takeout-requests/<int:pk>/container-list",
         ContainersForTakeoutView.as_view()),
    path("api/tank-takeout-requests", TankTakeoutRequestListView.as_view()),
    path("api/tank-takeout-requests/<int:pk>",
         TankTakeoutDetailView.as_view()),
    path("api/container-takeout-requests",
         ContainersTakeoutListView.as_view()),
    path("api/public-feedback", PublicFeedbackView.as_view()),
    path("api/building-parts", BuildingPartView.as_view()),
    path("api/takeout-conditions", TakeoutConditionListView.as_view()),
    path("api/takeout-conditions/<int:pk>",
         TakeoutConditionDetailView.as_view()),
    path("api/full-container-reports", FullContainerReportView.as_view()),
    path("api/collected-mass", CollectedMassView.as_view()),
    path("api/container-count", ContainerCountView.as_view())
]

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('api/schema/',
             SpectacularAPIView.as_view(),
             name='schema'),
        path('api/schema/swagger-ui/',
             SpectacularSwaggerView.as_view(url_name='schema'),
             name='swagger-ui'),
        path('api/schema/redoc/',
             SpectacularRedocView.as_view(url_name='schema'),
             name='redoc'),
    ]
