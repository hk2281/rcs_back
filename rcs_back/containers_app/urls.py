from django.urls import path

from .views import *


urlpatterns = [
    path("containers/<int:pk>/fill", FillContainerView.as_view())
]
