from django.contrib import admin

from .models import Assignment, AssignmentSubmission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "course",
        "teacher",
        "due_date",
        "total_marks",
        "created_at",
    )

    list_filter = (
        "course",
        "teacher",
        "due_date",
        "created_at",
    )

    search_fields = (
        "title",
        "course__code",
        "course__name",
        "teacher__user__first_name",
        "teacher__user__last_name",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (

        ("Assignment Information", {
            "fields": (
                "title",
                "description",
                "course",
                "teacher",
                "file",
            )
        }),

        ("Marks & Due Date", {
            "fields": (
                "total_marks",
                "due_date",
            )
        }),

        ("System Information", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),

    )


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):

    list_display = (
        "assignment",
        "student",
        "status",
        "marks",
        "submitted_at",
    )

    list_filter = (
        "status",
        "submitted_at",
        "assignment",
    )

    search_fields = (
        "assignment__title",
        "student__roll_no",
        "student__user__first_name",
        "student__user__last_name",
    )

    ordering = (
        "-submitted_at",
    )

    readonly_fields = (
        "submitted_at",
    )

    fieldsets = (

        ("Submission Details", {
            "fields": (
                "assignment",
                "student",
                "file",
            )
        }),

        ("Evaluation", {
            "fields": (
                "status",
                "marks",
                "feedback",
            )
        }),

        ("System Information", {
            "fields": (
                "submitted_at",
            )
        }),

    )

    actions = [
        "mark_submitted",
        "mark_late",
    ]

    def mark_submitted(self, request, queryset):

        queryset.update(status="SUBMITTED")

        self.message_user(
            request,
            f"{queryset.count()} submission(s) marked as Submitted."
        )

    mark_submitted.short_description = "Mark selected as Submitted"

    def mark_late(self, request, queryset):

        queryset.update(status="LATE")

        self.message_user(
            request,
            f"{queryset.count()} submission(s) marked as Late."
        )

    mark_late.short_description = "Mark selected as Late"