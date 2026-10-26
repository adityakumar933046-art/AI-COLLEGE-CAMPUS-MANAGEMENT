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

def send_email(subject, message, recipient):
    ok, _ = send_campus_email(to_email=recipient, subject=subject, text_content=message)
    return ok

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
        send_campus_email(
            to_email=user.email,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
        )
    except Exception as e:
        campus_email_logger.warning("Password reset OTP email failed for %s: %s", getattr(user, 'email', ''), str(e))

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
# CENTRAL SAFE EMAIL DISPATCHER (SMTP & HTTPS SUPPORT)
# ==========================================================

import logging
campus_email_logger = logging.getLogger("campus_email")


def send_campus_email(to_email, subject, text_content, html_content=None, from_email=None):
    """
    Robust central dispatcher for sending email across Smart Campus.
    Features:
    1. Resend HTTPS API (port 443) if RESEND_API_KEY is configured (bypasses SMTP, ideal for Render).
    2. Standard Django SMTP backend with explicit finite timeout (default 10s).
    3. Handles connection failures, SMTP exceptions, and socket timeouts without hanging Gunicorn.
    4. Logs useful diagnostic information without exposing credentials or secrets.
    Returns: (bool, str) -> (success, message_or_error)
    """
    import os
    import json
    import socket
    import smtplib
    import urllib.request
    import urllib.error
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives, get_connection

    sender = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'adityakumar933046@gmail.com'
    recipient = to_email.strip() if isinstance(to_email, str) else str(to_email)

    if not recipient:
        return False, "Recipient email address is missing."

    # --- Strategy A: HTTPS REST API (Resend) if configured ---
    resend_key = getattr(settings, 'RESEND_API_KEY', '') or os.environ.get('RESEND_API_KEY', '')
    if resend_key:
        try:
            campus_email_logger.info("Attempting email dispatch via Resend HTTPS API to %s", recipient)
            payload = {
                "from": sender,
                "to": [recipient],
                "subject": subject,
                "html": html_content or text_content,
            }
            if text_content:
                payload["text"] = text_content

            headers = {
                "Authorization": f"Bearer {resend_key.strip()}",
                "Content-Type": "application/json",
                "User-Agent": "SmartCampus/1.0",
            }
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=int(getattr(settings, 'EMAIL_TIMEOUT', None) or 10)) as resp:
                if 200 <= resp.status < 300:
                    campus_email_logger.info("Email sent successfully via Resend HTTPS API to %s", recipient)
                    return True, "Email sent successfully via HTTPS API."
                return False, f"HTTPS API returned status {resp.status}."
        except urllib.error.HTTPError as he:
            err_body = he.read().decode('utf-8', errors='ignore')
            campus_email_logger.warning("Resend HTTPS API error (%s): %s", he.code, err_body)
            # Fall through to SMTP if HTTPS API failed
        except Exception as exc:
            campus_email_logger.warning("Resend HTTPS API request exception: %s. Falling back to SMTP...", exc)

    # --- Strategy B: Django SMTP Backend with Finite Timeout Guard ---
    timeout_val = int(getattr(settings, 'EMAIL_TIMEOUT', None) or 10)
    host = getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com')
    port = int(getattr(settings, 'EMAIL_PORT', 587) or 587)

    try:
        connection = get_connection(timeout=timeout_val)
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=sender,
            to=[recipient],
            connection=connection,
        )
        if html_content:
            email_msg.attach_alternative(html_content, "text/html")

        email_msg.send(fail_silently=False)
        campus_email_logger.info("Email sent successfully via SMTP to %s", recipient)
        return True, "Credential email sent successfully."

    except (socket.timeout, TimeoutError):
        err_msg = f"Connection to SMTP server ({host}:{port}) timed out after {timeout_val}s. Outbound SMTP port may be blocked or unreachable from cloud host."
        campus_email_logger.warning("Email timeout for %s: %s", recipient, err_msg)
        return False, err_msg
    except smtplib.SMTPAuthenticationError as auth_err:
        err_msg = "SMTP authentication failed. Please verify EMAIL_HOST_USER and your Gmail App Password."
        campus_email_logger.warning("SMTP auth failed for %s: %s", recipient, str(auth_err))
        return False, err_msg
    except smtplib.SMTPServerDisconnected as disconn_err:
        err_msg = f"SMTP server disconnected unexpectedly ({disconn_err})."
        campus_email_logger.warning("SMTP disconnected for %s: %s", recipient, err_msg)
        return False, err_msg
    except (smtplib.SMTPConnectError, ConnectionRefusedError, OSError) as conn_err:
        err_msg = f"Could not connect to SMTP server ({host}:{port}): {conn_err}"
        campus_email_logger.warning("SMTP connection error for %s: %s", recipient, err_msg)
        return False, err_msg
    except smtplib.SMTPException as smtp_err:
        err_msg = f"SMTP protocol error: {str(smtp_err)}"
        campus_email_logger.warning("SMTP exception for %s: %s", recipient, err_msg)
        return False, err_msg
    except Exception as e:
        err_msg = f"Email delivery error: {str(e)}"
        campus_email_logger.error("Unexpected email error for %s: %s", recipient, err_msg)
        return False, err_msg


def send_account_credentials_email(user, temporary_password, role=None, request=None):
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
        login_url = "https://ai-college-campus-management.onrender.com/login/"

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
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'adityakumar933046@gmail.com'

        ok, msg = send_campus_email(
            to_email=user.email,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            from_email=from_email,
        )
        return ok, msg
    except Exception as e:
        return False, str(e)


def send_student_credentials_email(user, temporary_password, request=None):
    return send_account_credentials_email(user, temporary_password, role="STUDENT", request=request)


def send_teacher_credentials_email(user, temporary_password, request=None):
    return send_account_credentials_email(user, temporary_password, role="TEACHER", request=request)
