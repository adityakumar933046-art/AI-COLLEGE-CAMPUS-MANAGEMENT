from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "course",
        "teacher",
        "uploaded_at",
    )

    list_filter = (
        "course",
        "teacher",
        "uploaded_at",
    )

    search_fields = (
        "title",
        "description",
        "course__code",
        "course__name",
        "teacher__user__first_name",
        "teacher__user__last_name",
    )

    ordering = (
        "-uploaded_at",
    )

    readonly_fields = (
        "uploaded_at",
        "updated_at",
    )

    fieldsets = (

        ("Note Information", {
            "fields": (
                "title",
                "description",
                "course",
                "teacher",
                "file",
            )
        }),

        ("System Information", {
            "fields": (
                "uploaded_at",
                "updated_at",
            )
        }),

    )