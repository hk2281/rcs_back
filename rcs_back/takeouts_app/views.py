from rest_framework import generics

from .models import TakeoutRequest
from .serializers import TakeoutRequestSerializer


class TakeoutListView(generics.ListCreateAPIView):
    """CRUD для заявки на вынос"""
    serializer_class = TakeoutRequestSerializer
    queryset = TakeoutRequest.objects.all()
