from django.conf import settings
from django.contrib.auth import get_user_model
from djoser import signals
from djoser.conf import settings as djoser_settings
from djoser.compat import get_user_email
from djoser.serializers import UserCreateSerializer
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from rcs_back.users_app.models import RegistrationToken


User = get_user_model()


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


class ObtainRegistrationTokenView(APIView):
    """Получает новый токен для регистрации"""

    def get(self, request, *args, **kwargs):
        token = RegistrationToken.objects.create()
        token.set_token()
        token.save()

        resp = {}
        resp["token"] = token.token
        return Response(resp)


class CreateUserWithTokenView(generics.CreateAPIView):
    """Создание пользователя с проверкой токена"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """Проверяем токен"""
        submitted_token = self.request.query_params.get("token")
        token = RegistrationToken.objects.filter(
            token=submitted_token
        ).first()
        if token and not token.has_expired() and not token.is_claimed:

            """Код из djoser"""
            user = serializer.save()
            signals.user_registered.send(
                sender=self.__class__, user=user, request=self.request
            )
            context = {"user": user}
            to = [get_user_email(user)]
            if djoser_settings.SEND_ACTIVATION_EMAIL:
                djoser_settings.EMAIL.activation(
                    self.request, context).send(to)
            elif djoser_settings.SEND_CONFIRMATION_EMAIL:
                djoser_settings.EMAIL.confirmation(
                    self.request, context).send(to)

            """Токен использован"""
            token.is_claimed = True
            token.save()
        else:
            error_msg = "Invalid token."
            detail = {
                "error": error_msg
            }
            raise ValidationError(
                detail=detail, code=status.HTTP_400_BAD_REQUEST
            )
