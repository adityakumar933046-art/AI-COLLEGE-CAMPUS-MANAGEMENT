from django.contrib import admin

from .models import Timetable


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):

    list_display = (
        "course",
        "teacher",
        "department",
        "semester",
        "section",
        "day",
        "start_time",
        "end_time",
        "classroom",
        "is_active",
    )

    list_filter = (
        "department",
        "semester",
        "section",
        "day",
        "is_active",
    )

    search_fields = (
        "course__name",
        "course__code",
        "teacher__user__first_name",
        "teacher__user__last_name",
        "department__name",
        "classroom",
    )

    ordering = (
        "day",
        "start_time",
    )

    list_per_page = 20

    autocomplete_fields = (
        "department",
        "course",
        "teacher",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (

        (
            "Academic Information",
            {
                "fields": (
                    "department",
                    "semester",
                    "section",
                    "course",
                    "teacher",
                )
            },
        ),

        (
            "Schedule",
            {
                "fields": (
                    "day",
                    "start_time",
                    "end_time",
                    "classroom",
                )
            },
        ),

        (
            "Status",
            {
                "fields": (
                    "is_active",
                )
            },
        ),

        (
            "System Information",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),

    )