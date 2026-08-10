from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import (
    User,
    LoginHistory,
    ActivityLog,
    PasswordResetOTP,
    UserNotification,
)


# ==========================================================
# USER ADMIN
# ==========================================================

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "profile_preview",
        "username",
        "full_name",
        "email",
        "role",
        "phone",
        "is_verified",
        "is_active",
        "is_staff",
        "date_joined",
    )

    list_filter = (
        "role",
        "gender",
        "is_verified",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
    )

    ordering = (
        "username",
    )

    list_per_page = 25

    readonly_fields = (
        "profile_preview",
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
        "password_changed_at",
        "last_login_ip",
    )
    fieldsets = (

        ("Login Information", {
            "fields": (
                "username",
                "password",
            )
        }),

        ("Personal Information", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "phone",
                "profile_picture",
                "profile_preview",
                "date_of_birth",
                "gender",
                "address",
            )
        }),

        ("Role & Account Status", {
            "fields": (
                "role",
                "is_verified",
                "is_active_account",
            )
        }),

        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        ("Security", {
            "fields": (
                "password_changed_at",
                "last_login_ip",
            )
        }),

        ("Important Dates", {
            "fields": (
                "last_login",
                "date_joined",
                "created_at",
                "updated_at",
            )
        }),
    )

    add_fieldsets = (

        (
            "Create User",
            {
                "classes": ("wide",),

                "fields": (

                    "username",

                    "first_name",

                    "last_name",

                    "email",

                    "phone",

                    "role",

                    "password1",

                    "password2",

                    "is_verified",

                    "is_active",

                    "is_staff",

                ),
            },
        ),
    )

    actions = [

        "verify_users",

        "activate_users",

        "deactivate_users",

    ]

    def profile_preview(self, obj):

        if obj.profile_picture:

            return format_html(

                '<img src="{}" width="50" height="50" '
                'style="border-radius:50%;object-fit:cover;" />',

                obj.profile_picture.url,

            )

        return "No Image"

    profile_preview.short_description = "Profile"

        # ==========================================================
    # ADMIN ACTIONS
    # ==========================================================

    @admin.action(description="Verify selected users")
    def verify_users(self, request, queryset):

        updated = queryset.update(
            is_verified=True
        )

        self.message_user(
            request,
            f"{updated} user(s) verified successfully."
        )


    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):

        updated = queryset.update(
            is_active=True,
            is_active_account=True,
        )

        self.message_user(
            request,
            f"{updated} user(s) activated successfully."
        )


    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):

        updated = queryset.update(
            is_active=False,
            is_active_account=False,
        )

        self.message_user(
            request,
            f"{updated} user(s) deactivated successfully."
        )


# ==========================================================
# LOGIN HISTORY ADMIN
# ==========================================================

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "login_status",
        "login_time",
        "logout_time",
        "ip_address",
        "browser",
        "operating_system",
        "device",
        "session_key",
    )

    list_filter = (
        "login_status",
        "browser",
        "operating_system",
        "device",
        "login_time",
    )

    search_fields = (
        "user__username",
        "ip_address",
        "browser",
        "operating_system",
        "device",
    )

    ordering = (
        "-login_time",
    )

    list_per_page = 25

    readonly_fields = (
        "user",
        "login_status",
        "login_time",
        "logout_time",
        "ip_address",
        "browser",
        "operating_system",
        "device",
        "session_key",
    )

    # ==========================================================
# ACTIVITY LOG ADMIN
# ==========================================================

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "action",
        "module",
        "description",
        "ip_address",
        "created_at",
    )

    list_filter = (
        "action",
        "module",
        "created_at",
    )

    search_fields = (
        "user__username",
        "description",
        "module",
        "ip_address",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25

    readonly_fields = (
        "user",
        "action",
        "module",
        "description",
        "ip_address",
        "session_key",
        "created_at",
    )


# ==========================================================
# PASSWORD RESET OTP ADMIN
# ==========================================================

@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "otp",
        "created_at",
        "expires_at",
        "is_verified",
    )

    list_filter = (
        "is_verified",
        "created_at",
    )

    search_fields = (
        "user__username",
        "otp",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25

    readonly_fields = (
        "user",
        "otp",
        "created_at",
        "expires_at",
        "is_verified",
    )


# ==========================================================
# USER NOTIFICATION ADMIN
# ==========================================================

@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "title",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "user__username",
        "title",
        "message",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 25

    actions = [
        "mark_as_read",
        "mark_as_unread",
    ]

    @admin.action(description="Mark selected notifications as Read")
    def mark_as_read(self, request, queryset):

        updated = queryset.update(
            is_read=True
        )

        self.message_user(
            request,
            f"{updated} notification(s) marked as read."
        )

    @admin.action(description="Mark selected notifications as Unread")
    def mark_as_unread(self, request, queryset):

        updated = queryset.update(
            is_read=False
        )

        self.message_user(
            request,
            f"{updated} notification(s) marked as unread."
        )