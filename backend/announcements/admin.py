from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "target",
        "created_by",
        "created_at",
    )

    list_filter = (
        "target",
        "created_at",
    )

    search_fields = (
        "title",
        "message",
        "created_by__username",
        "created_by__first_name",
        "created_by__last_name",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (

        ("Announcement Information", {
            "fields": (
                "title",
                "message",
                "target",
                "created_by",
            )
        }),

        ("System Information", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),

    )

    actions = [
        "mark_for_all",
        "mark_for_students",
        "mark_for_teachers",
    ]

    def mark_for_all(self, request, queryset):

        queryset.update(target="ALL")

        self.message_user(
            request,
            f"{queryset.count()} announcement(s) updated for ALL."
        )

    mark_for_all.short_description = "Set target to ALL"

    def mark_for_students(self, request, queryset):

        queryset.update(target="STUDENT")

        self.message_user(
            request,
            f"{queryset.count()} announcement(s) updated for STUDENTS."
        )

    mark_for_students.short_description = "Set target to STUDENTS"

    def mark_for_teachers(self, request, queryset):

        queryset.update(target="TEACHER")

        self.message_user(
            request,
            f"{queryset.count()} announcement(s) updated for TEACHERS."
        )

    mark_for_teachers.short_description = "Set target to TEACHERS"