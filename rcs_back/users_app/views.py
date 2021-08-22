from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


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
