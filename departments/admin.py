from django.contrib import admin

from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "short_name",
        "hod",
        "office_phone",
        "office_email",
        "total_faculty",
        "total_students",
        "status",
        "is_imported",
        "created_at",
    )


    list_filter = (
        "status",
        "is_imported",
        "created_at",
        "established_year",
    )


    search_fields = (
        "code",
        "name",
        "short_name",
        "office_email",
        "office_phone",
        "hod__user__first_name",
        "hod__user__last_name",
    )


    ordering = (
        "name",
    )


    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "is_imported",
    )


    fieldsets = (

        (
            "Basic Information",
            {
                "fields": (
                    "code",
                    "name",
                    "short_name",
                    "description",
                    "established_year",
                    "logo",
                    "status",
                )
            }
        ),


        (
            "HOD Information",
            {
                "fields": (
                    "hod",
                    "hod_joining_date",
                )
            }
        ),


        (
            "Contact Information",
            {
                "fields": (
                    "office_phone",
                    "office_email",
                    "building",
                )
            }
        ),


        (
            "Statistics",
            {
                "fields": (
                    "total_faculty",
                    "total_students",
                )
            }
        ),


        (
            "Import Information",
            {
                "fields": (
                    "is_imported",
                )
            }
        ),


        (
            "Audit Information",
            {
                "fields": (
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                )
            }
        ),

    )


    actions = [
        "activate_departments",
        "deactivate_departments",
    ]


    def activate_departments(self, request, queryset):

        count = queryset.update(
            status="ACTIVE"
        )

        self.message_user(
            request,
            f"{count} department(s) activated successfully."
        )


    activate_departments.short_description = (
        "Activate selected departments"
    )


    def deactivate_departments(self, request, queryset):

        count = queryset.update(
            status="INACTIVE"
        )

        self.message_user(
            request,
            f"{count} department(s) deactivated successfully."
        )


    deactivate_departments.short_description = (
        "Deactivate selected departments"
    )