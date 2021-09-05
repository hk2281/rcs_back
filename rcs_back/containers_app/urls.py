from django.urls import path

from .views import *


urlpatterns = [
    path("", ContainerListView.as_view()),
    path("/public-add", ContainerPublicAddView.as_view()),
    path("/<int:pk>/activate", ActivateContainerView.as_view()),
    path("/<int:pk>", ContainerDetailView.as_view()),
    path("/<int:pk>/empty", EmptyContainerView.as_view()),
]
