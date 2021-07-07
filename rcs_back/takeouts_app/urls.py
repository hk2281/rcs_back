from django.urls import path

from .views import *


urlpatterns = [
    path("", TakeoutListView.as_view())
]
