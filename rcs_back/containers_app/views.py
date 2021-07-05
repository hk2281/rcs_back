from rest_framework import generics, permissions

from .models import Container
from .serializers import FillContainerSerializer


class FillContainerView(generics.UpdateAPIView):
    """ View для заполнения контейнера """
    permission_classes = [permissions.AllowAny]
    serializer_class = FillContainerSerializer
    queryset = Container.objects.filter(is_active=True)
