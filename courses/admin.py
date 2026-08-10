from django.contrib import admin
from .models import Course, CourseMaterial

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        'code',
        'name',
        'department',
        'teacher',
        'semester',
        'credits',
        'status',
    )

    list_filter = (
        'department',
        'semester',
        'status',
    )

    search_fields = (
        'code',
        'name',
        'department__name',
        'teacher__user__first_name',
        'teacher__user__last_name',
    )

    ordering = (
        'semester',
        'name',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fieldsets = (

        ("Course Information", {
            "fields": (
                "code",
                "name",
                "description",
            )
        }),

        ("Academic Information", {
            "fields": (
                "department",
                "teacher",
                "semester",
                "credits",
            )
        }),

        ("Status", {
            "fields": (
                "status",
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
        'activate_courses',
        'deactivate_courses',
    ]

    def activate_courses(self, request, queryset):

        queryset.update(status='ACTIVE')

        self.message_user(
            request,
            f"{queryset.count()} course(s) activated successfully."
        )

    activate_courses.short_description = "Activate selected courses"

    def deactivate_courses(self, request, queryset):

        queryset.update(status='INACTIVE')

        self.message_user(
            request,
            f"{queryset.count()} course(s) deactivated successfully."
        )

    deactivate_courses.short_description = "Deactivate selected courses"

# ==========================================
# COURSE MATERIAL ADMIN
# ==========================================

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "course",
        "uploaded_by",
        "uploaded_at",
    )

    list_filter = (
        "course",
        "uploaded_at",
    )

    search_fields = (
        "title",
        "course__name",
        "course__code",
    )

    readonly_fields = (
        "uploaded_at",
    )

    ordering = (
        "-uploaded_at",
    )