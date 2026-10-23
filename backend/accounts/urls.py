from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views import (
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)
urlpatterns = [

    # ==========================================================
    # HOME
    # ==========================================================

    path("", views.home, name="home"),

    # ==========================================================
    # AUTHENTICATION
    # ==========================================================

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),

    # ==========================================================
    # PROFILE
    # ==========================================================

    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("change-password/", views.change_password, name="change_password"),

    # ==========================================================
    # USER MANAGEMENT
    # ==========================================================

    path("users/", views.user_list, name="user_list"),
    path("users/<int:pk>/", views.user_detail, name="user_detail"),
    path("users/<int:pk>/edit/", views.user_update, name="user_update"),
    path("users/<int:pk>/delete/", views.user_delete, name="user_delete"),
    path("users/<int:pk>/activate/", views.activate_user, name="activate_user"),
    path("users/<int:pk>/deactivate/", views.deactivate_user, name="deactivate_user"),
    path("users/<int:pk>/toggle-status/", views.toggle_user_status, name="toggle_user_status"),

    # ==========================================================
    # PASSWORD RESET
    # ==========================================================

    path(
        "password-reset/",
        CustomPasswordResetView.as_view(),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),

    # ==========================================================
    # ERROR PAGE
    # ==========================================================

    path(
        "unauthorized/",
        views.unauthorized,
        name="unauthorized",
    ),

    # ==========================================================
    # FORGOT PASSWORD & OTP RESET
    # ==========================================================

    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
    path("verify-otp/", views.verify_otp_view, name="verify_otp"),
    path("resend-otp/", views.resend_otp_view, name="resend_otp"),
    path("reset-password/", views.reset_password_view, name="reset_password"),
]