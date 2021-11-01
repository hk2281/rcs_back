from django.urls import path

from .views import *

urlpatterns = [
    path("/containers", ContainerStatsExcelView.as_view()),
    path("/container-takeouts", ContainerTakeoutStatsExcelView.as_view()),
    path("/tank-takeouts", TankTakeoutStatsExcelView.as_view()),
    path("", AllStatsExcelView.as_view()),
]
