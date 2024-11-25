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
    AsignUserToBuildingsView,
    BuildingListView,
    BuildingPartView,
    BuildingAddView,
    BuildingDeleteView,
    BuildingUpdateView,
    AsignBuildingsToUserView,
    BuildingListPagiView,
    BuildingPartAddView,
    BuildingPartUpdateView,
    BuildingPartDeleteView,
    BuildingUsersView,
    ContainerCountView,
    FullContainerReportView,
    PublicFeedbackView,

)
from rcs_back.takeouts_app.views import (
    CollectedMassView,
    ContainersForTakeoutView,
    ContainersTakeoutDetailView,
    ContainersTakeoutListView,
    TakeoutConditionDetailView,
    TakeoutConditionListView,
    TankTakeoutDetailView,
    TankTakeoutRequestListView,
)
from rcs_back.users_app.views import RetrieveCurrentUserView, TemplateManager, UserListView


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/stats", include("rcs_back.stats_app.urls")),
    path("api/auth/users/me/", RetrieveCurrentUserView.as_view()),
#     path('api/auth/users/me/<int:pk>/',RetrieveCurrentUserView.as_view()),
    path ('api/auth/all-users', UserListView.as_view()),
    path('api/email-templates',TemplateManager.as_view()),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    path("api/containers", include("rcs_back.containers_app.urls")),
    path("api/buildings", BuildingListView.as_view()),
    path('api/buildings/pagi', BuildingListPagiView.as_view(), name='building-list-pagi'),
    path('api/buildings/<int:building_id>/users/', BuildingUsersView.as_view(), name='building-users'),
    path('api/buildings/create', BuildingAddView.as_view(), name='building-create'),
    path('api/buildings/delete/<int:pk>', BuildingDeleteView.as_view(), name='building-delete'),
    path('api/buildings/<int:pk>',BuildingUpdateView.as_view(), name='building-update'),
    path('api/buildings/asign-building-to-user/<int:user_id>',AsignBuildingsToUserView.as_view(), name='update-user-buildings'),
    path('api/buildings/asign-user-to-buildings/<int:building_id>', AsignUserToBuildingsView.as_view()),
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
    path('api/building-parts/create',BuildingPartAddView.as_view(), name='building-part-create'),
    path('api/building-parts/<int:pk>', BuildingPartUpdateView.as_view(), name='building-part-update'),
    path('api/building-parts/<int:pk>/delete', BuildingPartDeleteView.as_view(), name='building-part-delete'),
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
