from django.contrib import admin

from .models import *


admin.site.register(ContainersTakeoutRequest)
admin.site.register(ContainersTakeoutConfirmation)
admin.site.register(TankTakeoutRequest)
