from django.urls import path

from .views import (
    ContainerActivationRequestView,
    ContainerActivationView,
    ContainerDetailView,
    ContainerListView,
    ContainerPublicAddView,
    ContainerStickerView,
    EmptyContainerView,
)

urlpatterns = [
    path("", ContainerListView.as_view()),
    path("/public-add", ContainerPublicAddView.as_view()),
    path("/<int:pk>", ContainerDetailView.as_view()),
    path("/<int:pk>/empty", EmptyContainerView.as_view()),
    path("/<int:pk>/sticker", ContainerStickerView.as_view()),
    path("/<int:pk>/request-activation",
         ContainerActivationRequestView.as_view()),
    path("/<int:pk>/activate",
         ContainerActivationView.as_view()),
]
