from django.contrib import admin

from .models import (
    Building,
    BuildingPart,
    Container,
    EmailToken,
    FullContainerReport,
    TankTakeoutCompany,
)


class ContainerAdmin(admin.ModelAdmin):
    readonly_fields = [
        "mass",
        "activated_at",
        "avg_fill_time",
        "calc_avg_fill_time",
        "avg_takeout_wait_time",
        "cur_fill_time",
        "cur_takeout_wait_time",
        "last_full_report",
        "last_emptied_report",
        "ignore_reports_count",
        "is_full",
        "check_time_conditions",
        "requested_activation"
    ]


class BuildingPartAdmin(admin.ModelAdmin):
    readonly_fields = [
        "current_mass",
        "meets_mass_takeout_condition",
        "meets_time_takeout_condition",
        "needs_takeout",
        "containers_for_takeout",
        "container_count"
    ]


class BuildingAdmin(admin.ModelAdmin):
    readonly_fields = [
        "current_mass",
        "meets_mass_takeout_condition",
        "meets_time_takeout_condition",
        "needs_takeout",
        "containers_for_takeout",
        "container_count",
        "calculated_collected_mass",
        "confirmed_collected_mass",
        "avg_fill_speed"
    ]


class FullContainerReportAdmin(admin.ModelAdmin):
    readonly_fields = [
        "takeout_wait_time"
    ]


admin.site.register(Container, ContainerAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(BuildingPart, BuildingPartAdmin)
admin.site.register(FullContainerReport, FullContainerReportAdmin)
admin.site.register(EmailToken)
admin.site.register(TankTakeoutCompany)
