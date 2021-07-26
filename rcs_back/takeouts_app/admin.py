from django.contrib import admin

from .models import *


admin.site.register(ContainersTakeoutRequest)
admin.site.register(TankTakeoutRequest)
admin.site.register(TakeoutCompany)
admin.site.register(TakeoutCondition)
