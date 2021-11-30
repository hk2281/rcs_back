from django.urls import path

from .views import (
    AllStatsExcelView,
    ContainerStatsExcelView,
    ContainerTakeoutStatsExcelView,
    MonthlyActivationsPerBuildingView,
    MonthlyMassPerBuildingView,
    TankTakeoutStatsExcelView,
    YearlyMassPerBuildingView,
)

urlpatterns = [
    path("/containers", ContainerStatsExcelView.as_view()),
    path("/container-takeouts", ContainerTakeoutStatsExcelView.as_view()),
    path("/tank-takeouts", TankTakeoutStatsExcelView.as_view()),
    path("", AllStatsExcelView.as_view()),
    path("/mass-per-building/monthly", MonthlyMassPerBuildingView.as_view()),
    path("/mass-per-building/yearly", YearlyMassPerBuildingView.as_view()),
    path("/activations-per-building/monthly", MonthlyActivationsPerBuildingView.as_view())
]
