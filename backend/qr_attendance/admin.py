from django.contrib import admin

from .models import QRSession, QRAttendance


@admin.register(QRSession)
class QRSessionAdmin(admin.ModelAdmin):

    list_display = (
        "course",
        "teacher",
        "token",
        "status",
        "created_at",
        "expires_at",
        "attendance_count",
    )

    list_filter = (
        "status",
        "course",
        "teacher",
        "created_at",
    )

    search_fields = (
        "course__code",
        "course__name",
        "teacher__user__first_name",
        "teacher__user__last_name",
        "token",
    )

    readonly_fields = (
        "token",
        "created_at",
        "expires_at",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (

        ("QR Session", {
            "fields": (
                "course",
                "teacher",
                "token",
                "status",
            )
        }),

        ("Timing", {
            "fields": (
                "created_at",
                "expires_at",
            )
        }),

    )

    actions = [
        "activate_session",
        "close_session",
    ]

    def attendance_count(self, obj):
        return obj.attendance_records.count()

    attendance_count.short_description = "Scans"

    def activate_session(self, request, queryset):

        queryset.update(status="ACTIVE")

        self.message_user(
            request,
            f"{queryset.count()} session(s) activated."
        )

    activate_session.short_description = "Activate selected sessions"

    def close_session(self, request, queryset):

        queryset.update(status="CLOSED")

        self.message_user(
            request,
            f"{queryset.count()} session(s) closed."
        )

    close_session.short_description = "Close selected sessions"


@admin.register(QRAttendance)
class QRAttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "course_name",
        "teacher_name",
        "scanned_at",
    )

    list_filter = (
        "session__course",
        "session__teacher",
        "scanned_at",
    )

    search_fields = (
        "student__roll_no",
        "student__user__first_name",
        "student__user__last_name",
        "session__course__code",
        "session__course__name",
    )

    ordering = (
        "-scanned_at",
    )

    readonly_fields = (
        "scanned_at",
    )

    def course_name(self, obj):
        return obj.session.course.name

    course_name.short_description = "Course"

    def teacher_name(self, obj):
        return obj.session.teacher.user.get_full_name()

    teacher_name.short_description = "Teacher"