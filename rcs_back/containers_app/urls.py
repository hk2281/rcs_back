from django.urls import path

from .views import *


urlpatterns = [
    path("", ContainerListView.as_view()),
    path("/public-add", ContainerPublicAddView.as_view()),
    path("/status-options", ContainerStatusOptionsView.as_view()),
    path("/<int:pk>/fill", FillContainerView.as_view()),
    path("/<int:pk>/activate", ActivateContainerView.as_view()),
    path("/<int:pk>", ContainerDetailView.as_view()),
    path("/<int:pk>/sticker", GetStickerView.as_view())
]
