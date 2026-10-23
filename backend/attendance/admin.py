from django.contrib import admin

from .models import (
    AttendanceSession,
    Attendance,
)


# ======================================================
# ATTENDANCE SESSION ADMIN
# ======================================================

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "course",
        "department",
        "teacher",
        "semester",
        "section",
        "lecture_no",
        "attendance_date",
        "status",
        "created_at",
    )

    list_filter = (
        "department",
        "course",
        "teacher",
        "semester",
        "section",
        "status",
        "attendance_date",
    )

    search_fields = (
        "course__name",
        "course__code",
        "teacher__user__first_name",
        "teacher__user__last_name",
    )

    ordering = (
        "-attendance_date",
        "-lecture_no",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "attendance_date"

    list_per_page = 20


# ======================================================
# ATTENDANCE ADMIN
# ======================================================

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "student",
        "session",
        "status",
        "marked_by",
        "marked_at",
    )

    list_filter = (
        "status",
        "session__department",
        "session__course",
        "session__teacher",
        "session__semester",
        "session__section",
        "session__attendance_date",
    )

    search_fields = (
        "student__roll_no",
        "student__user__first_name",
        "student__user__last_name",
        "session__course__name",
    )

    ordering = (
        "-marked_at",
    )

    readonly_fields = (
        "marked_at",
        "updated_at",
    )

    list_per_page = 50

    autocomplete_fields = (
        "student",
        "session",
        "marked_by",
    )