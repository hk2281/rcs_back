from django.urls import path

from .views import *


urlpatterns = [
    path("<int:pk>/fill", FillContainerView.as_view()),
    path("<int:pk>", ContainerView.as_view())
]
