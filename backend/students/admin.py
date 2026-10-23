from django.contrib import admin
from django.utils.html import format_html

from .models import StudentProfile



@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):


    list_display = (

        "photo_preview",

        "roll_no",

        "admission_no",

        "user",

        "department",

        "semester",

        "section",

        "phone",

        "status",

        "cgpa",

        "is_imported",

    )


    list_filter = (

        "department",

        "semester",

        "status",

        "gender",

        "academic_year",

        "is_imported",

    )


    search_fields = (

        "roll_no",

        "admission_no",

        "user__username",

        "user__first_name",

        "user__last_name",

        "user__email",

        "phone",

        "father_name",

        "mother_name",

    )


    ordering = (
        "roll_no",
    )


    list_per_page = 25


    readonly_fields = (

        "photo_preview",

        "created_at",

        "updated_at",

        "is_imported",

        "created_by",

        "updated_by",

    )


    list_select_related = (

        "user",

        "department",

    )


    actions = [

        "activate_students",

        "deactivate_students",

    ]



    fieldsets = (


        (
            "Account Information",
            {
                "fields": (

                    "user",

                )
            }
        ),



        (
            "Academic Information",
            {
                "fields": (

                    "admission_no",

                    "roll_no",

                    "department",

                    "semester",

                    "section",

                    "batch",

                    "academic_year",

                    "cgpa",

                    "status",

                    "admission_date",

                )
            }
        ),



        (
            "Personal Information",
            {
                "fields": (

                    "photo",

                    "photo_preview",

                    "phone",

                    "gender",

                    "date_of_birth",

                    "blood_group",

                )
            }
        ),



        (
            "Guardian Information",
            {
                "fields": (

                    "father_name",

                    "mother_name",

                    "guardian_phone",

                )
            }
        ),



        (
            "Address",
            {
                "fields": (

                    "address",

                    "city",

                    "state",

                    "pincode",

                )
            }
        ),



        (
            "Import Information",
            {
                "classes": (
                    "collapse",
                ),

                "fields": (

                    "is_imported",

                )
            }
        ),



        (
            "Audit Information",
            {
                "classes": (
                    "collapse",
                ),

                "fields": (

                    "created_by",

                    "updated_by",

                    "created_at",

                    "updated_at",

                )
            }
        ),

    )



    def photo_preview(self, obj):

        if obj.photo:

            return format_html(

                '<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;">',

                obj.photo.url

            )


        return "No Photo"



    photo_preview.short_description = "Photo"




    def activate_students(self, request, queryset):

        count = queryset.update(
            status="ACTIVE"
        )


        self.message_user(

            request,

            f"{count} student(s) activated successfully."

        )



    activate_students.short_description = (
        "Activate selected students"
    )




    def deactivate_students(self, request, queryset):

        count = queryset.update(
            status="INACTIVE"
        )


        self.message_user(

            request,

            f"{count} student(s) deactivated successfully."

        )



    deactivate_students.short_description = (
        "Deactivate selected students"
    )



    def save_model(self, request, obj, form, change):

        if not change:

            obj.created_by = request.user


        obj.updated_by = request.user


        super().save_model(
            request,
            obj,
            form,
            change
        )