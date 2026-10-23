from students.models import StudentProfile
from teachers.models import TeacherProfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import (
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy

from .models import User

from .forms import (
    LoginForm,
    RegisterForm,
    UserUpdateForm,
    ProfileUpdateForm,
    CustomPasswordChangeForm,
)

from .decorators import (
    admin_required,
    teacher_required,
    student_required,
)

from .services import (
    save_login_history,
    save_failed_login,
    update_logout_history,
    log_login,
    log_logout,
    log_create,
)


# ==========================================================
# HOME
# ==========================================================

def home(request):

    if request.user.is_authenticated:

        if request.user.role == User.Roles.ADMIN:
            return redirect("admin_dashboard")

        elif request.user.role == User.Roles.TEACHER:
            return redirect("teacher_dashboard")

        return redirect("student_dashboard")

    return redirect("login")


# ==========================================================
# LOGIN
# ==========================================================

def login_view(request):

    if request.user.is_authenticated:

        if request.user.role == User.Roles.ADMIN:
            return redirect("admin_dashboard")

        elif request.user.role == User.Roles.TEACHER:
            return redirect("teacher_dashboard")
        return redirect("student_dashboard")

    form = LoginForm(request.POST or None, request = request,)

    if request.method == "POST":

        if form.is_valid():
            

            user = form.cleaned_data["user"]

            login(request, user)

            # Remember Me
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)

            # Save Login History
            save_login_history(
                request=request,
                user=user,
            )

            # Save Activity Log
            log_login(
                user=user,
                request=request,
            )

            messages.success(
                request,
                f"Welcome {user.full_name}!"
            )

            if user.role == User.Roles.ADMIN:
                return redirect("admin_dashboard")

            elif user.role == User.Roles.TEACHER:
                return redirect("teacher_dashboard")

            return redirect("student_dashboard")

        else:

            login_id = request.POST.get("username", "")

            if login_id:
                save_failed_login(
                    username=login_id,
                    request=request,
                )

            messages.error(
                request,
                "Invalid username/email or password."
            )

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
        },
    )


# ==========================================================
# LOGOUT
# ==========================================================

@login_required
def logout_view(request):

    # Save logout history
    update_logout_history(request)

    # Save activity log
    log_logout(
        user=request.user,
        request=request,
    )

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect("login")


# ==========================================================
# REGISTER
# ==========================================================

@login_required
@admin_required
def register_view(request):

    form = RegisterForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            user = form.save()

            log_create(
                user=request.user,
                request=request,
                module="Accounts",
                description=f"Created user '{user.username}'.",
            )

            messages.success(
                request,
                f"{user.username} registered successfully."
            )

            return redirect("user_list")

    return render(

        request,

        "accounts/register.html",

        {

            "form": form,

        },

    )


# ==========================================================
# PROFILE
# ==========================================================

@login_required
@login_required
# ==========================================================
# MY PROFILE (ROLE-AWARE & SECURE)
# ==========================================================
@login_required
def profile(request):
    user = request.user
    student_profile = None
    teacher_profile = None

    if user.role == "STUDENT":
        student_profile = getattr(user, 'student_profile', None)
        if not student_profile:
            student_profile = StudentProfile.objects.filter(user=user).first()
    elif user.role == "TEACHER":
        teacher_profile = getattr(user, 'teacher_profile', None)
        if not teacher_profile:
            teacher_profile = TeacherProfile.objects.filter(user=user).first()

    context = {
        "user_obj": user,
        "role": user.role,
        "student": student_profile,
        "teacher": teacher_profile,
        "title": f"{user.get_full_name() or user.username}'s Profile",
    }
    return render(request, "accounts/profile.html", context)


# ==========================================================
# EDIT PROFILE
# ==========================================================

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form": form,
            "title": "Edit Profile",
        },
    )

# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@login_required
def change_password(request):

    form = CustomPasswordChangeForm(
        request.user,
        request.POST or None,
    )

    if request.method == "POST":

        if form.is_valid():

            user = form.save()

            user.must_change_password = False
            user.save()

            update_session_auth_hash(
                request,
                user,
            )

            messages.success(
                request,
                "Password changed successfully."
            )

            if user.role == "ADMIN":
                return redirect("admin_dashboard")
            elif user.role == "TEACHER":
                return redirect("teacher_dashboard")
            return redirect("student_dashboard")

    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form,
        },
    )


# ==========================================================
# USER LIST
# ==========================================================

@login_required
@admin_required
def user_list(request):

    users = User.objects.all().order_by("username")

    search = request.GET.get("search")

    role = request.GET.get("role")

    if search:

        users = users.filter(

            username__icontains=search

        )

    if role:

        users = users.filter(

            role=role

        )

    context = {

        "users": users,

        "search": search,

        "role": role,

    }

    return render(

        request,

        "accounts/user_list.html",

        context,

    )


# ==========================================================
# USER DETAIL
# ==========================================================

@login_required
@admin_required
def user_detail(request, pk):

    user = get_object_or_404(

        User,

        pk=pk,

    )

    return render(

        request,

        "accounts/user_detail.html",

        {

            "user_obj": user,

        },

    )


# ==========================================================
# USER UPDATE
# ==========================================================

@login_required
@admin_required
def user_update(request, pk):

    user = get_object_or_404(

        User,

        pk=pk,

    )

    form = UserUpdateForm(

        request.POST or None,

        instance=user,

    )

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(

                request,

                "User updated successfully."

            )

            return redirect("user_list")

    return render(

        request,

        "accounts/user_update.html",

        {

            "form": form,

            "user_obj": user,

        },

    )

# ==========================================================
# USER DELETE
# ==========================================================

@login_required
@admin_required
def user_delete(request, pk):

    user = get_object_or_404(
        User,
        pk=pk,
    )

    if user == request.user:

        messages.error(
            request,
            "You cannot delete your own account."
        )

        return redirect("user_list")

    if request.method == "POST":

        username = user.username

        user.delete()

        messages.success(
            request,
            f"{username} deleted successfully."
        )

        return redirect("user_list")

    return render(
        request,
        "accounts/user_delete.html",
        {
            "user_obj": user,
        },
    )


# ==========================================================
# ACTIVATE USER
# ==========================================================

@login_required
@admin_required
def activate_user(request, pk):

    user = get_object_or_404(
        User,
        pk=pk,
    )

    user.is_active = True
    user.is_active_account = True
    user.save(
        update_fields=[
            "is_active",
            "is_active_account",
        ]
    )

    messages.success(
        request,
        f"{user.username} activated successfully."
    )

    return redirect("user_list")


# ==========================================================
# DEACTIVATE USER
# ==========================================================

@login_required
@admin_required
def deactivate_user(request, pk):

    user = get_object_or_404(
        User,
        pk=pk,
    )

    if user == request.user:

        messages.error(
            request,
            "You cannot deactivate your own account."
        )

        return redirect("user_list")

    user.is_active = False
    user.is_active_account = False

    user.save(
        update_fields=[
            "is_active",
            "is_active_account",
        ]
    )

    messages.success(
        request,
        f"{user.username} deactivated successfully."
    )

    return redirect("user_list")


# ==========================================================
# TOGGLE USER STATUS
# ==========================================================

@login_required
@admin_required
def toggle_user_status(request, pk):

    user = get_object_or_404(
        User,
        pk=pk,
    )

    if user == request.user:

        messages.error(
            request,
            "You cannot modify your own account."
        )

        return redirect("user_list")

    user.is_active = not user.is_active
    user.is_active_account = user.is_active

    user.save(
        update_fields=[
            "is_active",
            "is_active_account",
        ]
    )

    if user.is_active:

        messages.success(
            request,
            "User activated successfully."
        )

    else:

        messages.warning(
            request,
            "User deactivated successfully."
        )

    return redirect("user_list")


# ==========================================================
# UNAUTHORIZED
# ==========================================================

@login_required
def unauthorized(request):

    return render(
        request,
        "accounts/unauthorized.html",
        status=403,
    )


# ==========================================================
# PASSWORD RESET VIEWS
# ==========================================================

class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.txt"
    html_email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")


class CustomPasswordResetDoneView(
    PasswordResetDoneView
):

    template_name = (
        "accounts/password_reset_done.html"
    )


class CustomPasswordResetConfirmView(
    PasswordResetConfirmView
):

    template_name = (
        "accounts/password_reset_confirm.html"
    )

    success_url = reverse_lazy(
        "password_reset_complete"
    )


class CustomPasswordResetCompleteView(
    PasswordResetCompleteView
):

    template_name = (
        "accounts/password_reset_complete.html"
    )

# ==========================================================
# PHASE 6 — FORGOT PASSWORD & OTP RESET VIEWS
# ==========================================================

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .services import create_password_reset_otp, verify_password_reset_otp, reset_user_password_with_otp


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if email:
            user = User.objects.filter(email__iexact=email, is_active=True, is_active_account=True).first()
            if user:
                create_password_reset_otp(user)

            request.session["reset_email"] = email
            messages.info(request, "If an account exists for this email, a verification code has been sent.")
            return redirect("verify_otp")

    return render(request, "accounts/forgot_password.html")


def verify_otp_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    email = request.session.get("reset_email")
    if not email:
        messages.error(request, "Please enter your email address first.")
        return redirect("forgot_password")

    if request.method == "POST":
        otp = request.POST.get("otp", "").strip()
        user = User.objects.filter(email__iexact=email, is_active=True, is_active_account=True).first()

        if user:
            verified, msg = verify_password_reset_otp(user, otp)
            if verified:
                request.session["otp_verified"] = True
                request.session["reset_user_id"] = user.id
                messages.success(request, "Verification code verified successfully. Please set your new password.")
                return redirect("reset_password")
            else:
                messages.error(request, msg)
        else:
            messages.error(request, "Invalid verification code. Please try again.")

    masked_email = email
    if "@" in email:
        name_part, domain_part = email.split("@", 1)
        masked_name = name_part[0] + "***" if len(name_part) > 1 else "*"
        masked_email = f"{masked_name}@{domain_part}"

    return render(request, "accounts/verify_otp.html", {"email": masked_email})


def resend_otp_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    email = request.session.get("reset_email")
    if not email:
        messages.error(request, "Please enter your email address first.")
        return redirect("forgot_password")

    user = User.objects.filter(email__iexact=email, is_active=True, is_active_account=True).first()
    if user:
        ok, msg, _ = create_password_reset_otp(user)
        if ok:
            messages.success(request, "A new verification code has been sent to your email.")
        else:
            messages.warning(request, msg)
    else:
        messages.info(request, "If an account exists for this email, a verification code has been sent.")

    return redirect("verify_otp")


def reset_password_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if not request.session.get("otp_verified") or not request.session.get("reset_user_id"):
        messages.error(request, "Please verify your code first.")
        return redirect("forgot_password")

    user_id = request.session.get("reset_user_id")
    user = User.objects.filter(id=user_id, is_active=True, is_active_account=True).first()

    if not user:
        messages.error(request, "User account not found or inactive.")
        return redirect("forgot_password")

    if request.method == "POST":
        pwd1 = request.POST.get("new_password1", "")
        pwd2 = request.POST.get("new_password2", "")

        if not pwd1 or not pwd2:
            messages.error(request, "Password fields cannot be empty.")
        elif pwd1 != pwd2:
            messages.error(request, "Passwords do not match.")
        else:
            try:
                validate_password(pwd1, user=user)
                ok, msg = reset_user_password_with_otp(user, pwd1)
                if ok:
                    # Clean up session
                    request.session.pop("reset_email", None)
                    request.session.pop("otp_verified", None)
                    request.session.pop("reset_user_id", None)
                    messages.success(request, "Password reset successfully. You can now log in with your new password.")
                    return redirect("login")
                else:
                    messages.error(request, msg)
            except DjangoValidationError as ve:
                for err in ve.messages:
                    messages.error(request, err)

    return render(request, "accounts/reset_password.html")
