from django.conf import settings
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from rcs_back.users_app.models import User
from .serializers import *


class RetrieveCurrentUserView(APIView):
    """Возвращает информацию о текущем пользователе"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        has_eco_group = False
        if request.user.groups.filter(name=settings.ECO_GROUP):
            has_eco_group = True

        resp = {}
        resp["id"] = request.user.pk
        resp["email"] = request.user.email
        resp["has_eco_group"] = has_eco_group
        return Response(resp)


class UnconfirmedUserListView(generics.ListAPIView):
    """Список пользователей, которые не были подтверждены"""
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.query_params.get("is_confirmed"):
            return User.objects.filter(
                is_confirmed=False
            )
        else:
            return User.objects.none()


class ConfirmUserView(generics.UpdateAPIView):
    """View для подтверждения пользователя"""
    serializer_class = UserSerializer
    queryset = User.objects.filter(
        is_confirmed=False
    )


class TokenObtainPairView(TokenViewBase):
    serializer_class = TokenObtainPairSerializer
