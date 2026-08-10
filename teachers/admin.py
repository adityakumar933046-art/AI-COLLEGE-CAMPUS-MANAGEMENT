from django.contrib import admin
from django.utils.html import format_html

from .models import TeacherProfile


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):

    list_display = (
        "photo_preview",
        "employee_id",
        "full_name",
        "department",
        "designation",
        "phone",
        "employment_type",
        "status",
        "is_hod",
    )

    list_filter = (
        "department",
        "designation",
        "employment_type",
        "status",
        "gender",
        "is_hod",
    )

    search_fields = (
        "employee_id",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "phone",
        "qualification",
        "specialization",
    )

    ordering = ("employee_id",)

    list_per_page = 25

    list_select_related = (
        "user",
        "department",
        "created_by",
        "updated_by",
    )

    date_hierarchy = "joining_date"

    save_on_top = True

    autocomplete_fields = (
        "user",
        "department",
        "created_by",
        "updated_by",
    )

    readonly_fields = (
        "photo_preview",
        "created_at",
        "updated_at",
    )

    fieldsets = (

        ("Account Information", {
            "fields": (
                "user",
                "employee_id",
            )
        }),

        ("Professional Information", {
            "fields": (
                "department",
                "designation",
                "qualification",
                "specialization",
                "experience",
                "employment_type",
                "joining_date",
                "office_room",
                "is_hod",
                "status",
            )
        }),

        ("Personal Information", {
            "fields": (
                "photo",
                "photo_preview",
                "phone",
                "gender",
                "date_of_birth",
                "blood_group",
            )
        }),

        ("Audit Information", {
            "classes": ("collapse",),
            "fields": (
                "created_by",
                "updated_by",
                "created_at",
                "updated_at",
            )
        }),

    )

    actions = (
        "activate_teachers",
        "deactivate_teachers",
    )

    def full_name(self, obj):
        return obj.user.get_full_name()

    full_name.short_description = "Full Name"

    def photo_preview(self, obj):

        if obj.photo and hasattr(obj.photo, "url"):

            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;">',
                obj.photo.url,
            )

        return "No Photo"

    photo_preview.short_description = "Photo"

    def activate_teachers(self, request, queryset):

        updated = queryset.update(status="ACTIVE")

        self.message_user(
            request,
            f"{updated} teacher(s) activated successfully."
        )

    activate_teachers.short_description = "Activate selected teachers"

    def deactivate_teachers(self, request, queryset):

        updated = queryset.update(status="INACTIVE")

        self.message_user(
            request,
            f"{updated} teacher(s) deactivated successfully."
        )

    deactivate_teachers.short_description = "Deactivate selected teachers"

    def get_queryset(self, request):

        return super().get_queryset(request).select_related(
            "user",
            "department",
            "created_by",
            "updated_by",
        )

    def save_model(self, request, obj, form, change):

        if not change and not obj.created_by:
            obj.created_by = request.user

        obj.updated_by = request.user

        super().save_model(
            request,
            obj,
            form,
            change,
        )