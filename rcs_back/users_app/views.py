from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class RetrieveCurrentUserView(APIView):
    """Возвращает информацию о текущем пользователе"""

    def get(self, request, *args, **kwargs):

        has_eco_group = False
        if request.user.groups.filter(name=settings.ECO_GROUP):
            has_eco_group = True

        resp = {}
        resp["id"] = request.user.pk
        resp["email"] = request.user.email
        resp["has_eco_group"] = has_eco_group
        if request.user.building:
            resp["building"] = request.user.building.pk
        else:
            resp["building"] = None
        return Response(resp)
