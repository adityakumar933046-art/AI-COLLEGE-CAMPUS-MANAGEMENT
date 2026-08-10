import random
import secrets
import string

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import (
    LoginHistory,
    ActivityLog,
    PasswordResetOTP,
    UserNotification,
)

User = get_user_model()


# ==========================================================
# PASSWORD GENERATOR
# ==========================================================

def generate_secure_password(length=10):

    alphabet = (
        string.ascii_letters +
        string.digits +
        "@#$%&*!"
    )

    while True:

        password = "".join(
            secrets.choice(alphabet)
            for _ in range(length)
        )

        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "@#$%&*!" for c in password)
        ):

            return password


# ==========================================================
# OTP GENERATOR
# ==========================================================

def generate_otp():

    return str(
        random.randint(100000, 999999)
    )


# ==========================================================
# SEND EMAIL
# ==========================================================

def send_email(

    subject,

    message,

    recipient,

):

    send_mail(

        subject,

        message,

        settings.DEFAULT_FROM_EMAIL,

        [recipient],

        fail_silently=False,

    )

from django.db import transaction


# ==========================================================
# CREATE USER
# ==========================================================

@transaction.atomic
def create_user(data):

    errors = []

    username = data.get("username", "").strip()

    email = data.get("email", "").strip().lower()

    if User.objects.filter(username__iexact=username).exists():

        errors.append("Username already exists.")

    if User.objects.filter(email__iexact=email).exists():

        errors.append("Email already exists.")

    if errors:

        return {

            "success": False,

            "errors": errors,

        }

    password = data.get("password")

    if not password:

        password = generate_secure_password()

    user = User.objects.create_user(

        username=username,

        first_name=data.get("first_name", ""),

        last_name=data.get("last_name", ""),

        email=email,

        phone=data.get("phone", ""),

        role=data.get("role", User.Roles.STUDENT),

        password=password,

    )

    user.is_verified = data.get(
        "is_verified",
        False,
    )

    user.is_active_account = True

    user.save()

    ActivityLog.objects.create(

        user=user,

        action=ActivityLog.Actions.CREATE,

        module="Accounts",

        description=f"User account created for {user.username}",

    )

    return {

        "success": True,

        "user": user,

        "username": user.username,

        "password": password,

    }

# ==========================================================
# LOGIN HISTORY SERVICES
# ==========================================================

def save_login_history(

    request,

    user,

    login_status=LoginHistory.LoginStatus.SUCCESS,

):

    user_agent = request.META.get(
        "HTTP_USER_AGENT",
        ""
    )

    ip_address = request.META.get(
        "REMOTE_ADDR"
    )

    session_key = request.session.session_key

    history = LoginHistory.objects.create(

        user=user,

        login_status=login_status,

        ip_address=ip_address,

        browser=user_agent[:255],

        operating_system=user_agent[:255],

        device=user_agent[:100],

        session_key=session_key,

    )

    user.last_login_ip = ip_address

    user.save(update_fields=["last_login_ip"])

    return history


# ==========================================================
# UPDATE LOGOUT TIME
# ==========================================================

def update_logout_history(request):

    session_key = request.session.session_key

    if not session_key:

        return

    history = LoginHistory.objects.filter(

        session_key=session_key,

        logout_time__isnull=True,

    ).first()

    if history:

        history.logout_time = timezone.now()

        history.save(
            update_fields=["logout_time"]
        )


# ==========================================================
# FAILED LOGIN
# ==========================================================

def save_failed_login(

    username,

    request,

):

    try:

        user = User.objects.get(
            username__iexact=username
        )

    except User.DoesNotExist:

        return

    save_login_history(

        request=request,

        user=user,

        login_status=LoginHistory.LoginStatus.FAILED,

    )


    # ==========================================================
# ACTIVITY LOG SERVICES
# ==========================================================

def log_activity(

    user,

    action,

    description,

    request=None,

    module="General",

):

    ip_address = None

    session_key = None

    if request:

        ip_address = request.META.get(
            "REMOTE_ADDR"
        )

        if not request.session.session_key:
            request.session.save()

        session_key = request.session.session_key or ""

    return ActivityLog.objects.create(

        user=user,

        action=action,

        module=module,

        description=description,

        ip_address=ip_address,

        session_key=session_key,

    )


# ==========================================================
# COMMON ACTIVITY FUNCTIONS
# ==========================================================

def log_login(user, request):

    return log_activity(

        user=user,

        action=ActivityLog.Actions.LOGIN,

        module="Accounts",

        description="User logged in.",

        request=request,

    )


def log_logout(user, request):

    return log_activity(

        user=user,

        action=ActivityLog.Actions.LOGOUT,

        module="Accounts",

        description="User logged out.",

        request=request,

    )


def log_profile_update(user, request):

    return log_activity(

        user=user,

        action=ActivityLog.Actions.PROFILE_UPDATE,

        module="Accounts",

        description="Profile updated.",

        request=request,

    )


def log_password_change(user, request):

    user.password_changed_at = timezone.now()

    user.save(update_fields=["password_changed_at"])

    return log_activity(

        user=user,

        action=ActivityLog.Actions.PASSWORD_CHANGE,

        module="Accounts",

        description="Password changed.",

        request=request,

    )


def log_create(user, request, module, description):

    return log_activity(

        user=user,

        action=ActivityLog.Actions.CREATE,

        module=module,

        description=description,

        request=request,

    )


def log_update(user, request, module, description):

    return log_activity(

        user=user,

        action=ActivityLog.Actions.UPDATE,

        module=module,

        description=description,

        request=request,

    )


def log_delete(user, request, module, description):

    return log_activity(

        user=user,

        action=ActivityLog.Actions.DELETE,

        module=module,

        description=description,

        request=request,

    )

# ==========================================================
# PASSWORD RESET SERVICES
# ==========================================================

from datetime import timedelta




# ==========================================================
# PHASE 6 — FORGOT PASSWORD & OTP RESET SERVICES
# ==========================================================

import secrets
from datetime import timedelta
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import PasswordResetOTP, User


def create_password_reset_otp(user):
    """
    Generate a 6-digit OTP for password reset with 60-second resend cooldown
    and 10-minute expiration. Sends verification email dynamically.
    """
    if not user or not user.is_active or not getattr(user, 'is_active_account', True):
        # Email enumeration protection: return generic status
        return True, "If an account exists for this email, a verification code has been sent.", None

    # Check resend cooldown (60 seconds)
    existing_otp = PasswordResetOTP.objects.filter(user=user, is_verified=False).order_by('-created_at').first()
    if existing_otp and (timezone.now() - existing_otp.last_resend_at) < timedelta(seconds=60):
        return False, "Please wait at least 60 seconds before requesting another verification code.", existing_otp

    # Remove old unverified OTPs
    PasswordResetOTP.objects.filter(user=user, is_verified=False).delete()

    # Generate secure 6-digit OTP
    otp_code = str(secrets.randbelow(900000) + 100000)
    expires = timezone.now() + timedelta(minutes=10)

    otp_obj = PasswordResetOTP.objects.create(
        user=user,
        otp=otp_code,
        expires_at=expires,
        attempts=0,
        last_resend_at=timezone.now(),
    )

    # Render & send OTP email
    recipient_name = user.get_full_name().strip() or user.username
    context = {
        "name": recipient_name,
        "otp": otp_code,
        "expires_in_minutes": 10,
    }

    try:
        subject = "Smart Campus - Password Reset Verification Code"
        text_content = render_to_string("emails/password_reset_otp.txt", context)
        html_content = render_to_string("emails/password_reset_otp.html", context)

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@smartcampus.edu')
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[user.email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send(fail_silently=False)
    except Exception as e:
        # Do not log secrets or throw 500
        pass

    return True, "If an account exists for this email, a verification code has been sent.", otp_obj


def verify_password_reset_otp(user, otp):
    """
    Verify OTP with 5-attempt limit, expiration check, and single-use invalidation.
    """
    if not user:
        return False, "Invalid verification request."

    otp_obj = PasswordResetOTP.objects.filter(user=user, is_verified=False).order_by('-created_at').first()

    if not otp_obj:
        return False, "Invalid verification code. Please request a new code."

    if otp_obj.attempts >= 5:
        return False, "Too many failed attempts. Please request a new verification code."

    if timezone.now() > otp_obj.expires_at:
        return False, "This verification code has expired. Please request a new code."

    if otp_obj.otp != str(otp).strip():
        otp_obj.attempts += 1
        otp_obj.save(update_fields=['attempts'])
        if otp_obj.attempts >= 5:
            return False, "Too many failed attempts. Please request a new verification code."
        return False, f"Invalid verification code. ({5 - otp_obj.attempts} attempts remaining)"

    # Mark verified
    otp_obj.is_verified = True
    otp_obj.save(update_fields=['is_verified'])
    return True, "Verification code verified successfully."


def reset_user_password_with_otp(user, new_password):
    """
    Reset user password, clear must_change_password flag, and cleanup OTPs.
    """
    if not user:
        return False, "User account not found."

    user.set_password(new_password)
    user.must_change_password = False
    user.save()

    # Clean up OTPs
    PasswordResetOTP.objects.filter(user=user).delete()
    return True, "Password reset successfully. You can now log in with your new password."


# ==========================================================
# CREATE USER NOTIFICATION
# ==========================================================

def create_notification(user, title, message):
    from .models import UserNotification
    try:
        return UserNotification.objects.create(
            user=user,
            title=title,
            message=message,
        )
    except Exception:
        return None


# ==========================================================
# UNIFIED SHARED ACCOUNT CREDENTIALS EMAIL SERVICE
# ==========================================================

def send_account_credentials_email(user, temporary_password, role=None, request=None):
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.conf import settings
    from django.urls import reverse

    if not user or not user.email:
        return False, "Recipient email address is missing."

    user_role = (role or getattr(user, 'role', '') or '').upper()
    if user_role in ['TEACHER', 'FACULTY']:
        role_display = "Faculty"
        subject = "Welcome to Smart Campus - Your Faculty Login Credentials"
    else:
        role_display = "Student"
        subject = "Welcome to Smart Campus - Your Student Login Credentials"

    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    if not site_url and request:
        login_path = reverse('login')
        login_url = request.build_absolute_uri(login_path)
    elif site_url:
        login_url = f"{site_url}{reverse('login')}"
    else:
        login_url = "http://127.0.0.1:8000/login/"

    recipient_name = user.get_full_name().strip() or user.username

    context = {
        "name": recipient_name,
        "username": user.username,
        "temporary_password": temporary_password,
        "role_display": role_display,
        "login_url": login_url,
    }

    try:
        text_content = render_to_string("emails/account_credentials.txt", context)
        html_content = render_to_string("emails/account_credentials.html", context)

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@smartcampus.edu')
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[user.email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send(fail_silently=False)

        return True, "Credential email sent successfully."
    except Exception as e:
        return False, str(e)


def send_student_credentials_email(user, temporary_password, request=None):
    return send_account_credentials_email(user, temporary_password, role="STUDENT", request=request)


def send_teacher_credentials_email(user, temporary_password, request=None):
    return send_account_credentials_email(user, temporary_password, role="TEACHER", request=request)
