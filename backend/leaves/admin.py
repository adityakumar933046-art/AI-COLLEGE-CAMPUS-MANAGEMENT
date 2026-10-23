from django.contrib import admin

from .models import Leave


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):

    list_display = (
        "applicant",
        "from_date",
        "to_date",
        "status",
        "applied_at",
    )

    list_filter = (
        "status",
        "from_date",
        "to_date",
        "applied_at",
    )

    search_fields = (
        "applicant__username",
        "applicant__first_name",
        "applicant__last_name",
        "reason",
    )

    ordering = (
        "-applied_at",
    )

    readonly_fields = (
        "applied_at",
        "updated_at",
    )

    fieldsets = (

        ("Applicant Information", {
            "fields": (
                "applicant",
            )
        }),

        ("Leave Details", {
            "fields": (
                "from_date",
                "to_date",
                "reason",
            )
        }),

        ("Approval", {
            "fields": (
                "status",
                "remarks",
            )
        }),

        ("System Information", {
            "fields": (
                "applied_at",
                "updated_at",
            )
        }),

    )

    actions = [
        "approve_leave",
        "reject_leave",
    ]

    def approve_leave(self, request, queryset):

        queryset.update(
            status="APPROVED"
        )

        self.message_user(
            request,
            f"{queryset.count()} leave request(s) approved."
        )

    approve_leave.short_description = "Approve selected leave requests"

    def reject_leave(self, request, queryset):

        queryset.update(
            status="REJECTED"
        )

        self.message_user(
            request,
            f"{queryset.count()} leave request(s) rejected."
        )

    reject_leave.short_description = "Reject selected leave requests"
