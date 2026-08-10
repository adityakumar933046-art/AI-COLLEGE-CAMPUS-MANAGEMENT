from django.contrib import admin

from .models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "course",
        "semester",
        "marks_obtained",
        "total_marks",
        "percentage",
        "grade",
        "teacher",
    )

    list_filter = (
        "semester",
        "grade",
        "course",
        "teacher",
        "created_at",
    )

    search_fields = (
        "student__roll_no",
        "student__user__first_name",
        "student__user__last_name",
        "course__code",
        "course__name",
        "teacher__user__first_name",
        "teacher__user__last_name",
    )

    ordering = (
        "-semester",
        "student__roll_no",
    )

    readonly_fields = (
        "percentage",
        "grade",
        "created_at",
        "updated_at",
    )

    fieldsets = (

        ("Student Information", {
            "fields": (
                "student",
                "course",
                "teacher",
                "semester",
            )
        }),

        ("Marks", {
            "fields": (
                "marks_obtained",
                "total_marks",
                "percentage",
                "grade",
            )
        }),

        ("Remarks", {
            "fields": (
                "remarks",
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
        "mark_pass",
        "mark_fail",
    ]

    def mark_pass(self, request, queryset):

        queryset.exclude(
            grade="F"
        ).update(
            remarks="Passed"
        )

        self.message_user(
            request,
            f"{queryset.count()} result(s) marked as Passed."
        )

    mark_pass.short_description = "Mark selected as Passed"

    def mark_fail(self, request, queryset):

        queryset.update(
            grade="F",
            remarks="Failed"
        )

        self.message_user(
            request,
            f"{queryset.count()} result(s) marked as Failed."
        )

    mark_fail.short_description = "Mark selected as Failed"