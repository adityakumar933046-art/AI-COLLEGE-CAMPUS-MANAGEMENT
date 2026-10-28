import os
import logging
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


def _sanitize_error(err_str, secrets=None):
    """Remove sensitive keys, client secrets, passwords, or tokens from error strings."""
    if not err_str:
        return ""
    clean = str(err_str)
    if secrets:
        for s in secrets:
            if s and len(s) > 3:
                clean = clean.replace(s, "[REDACTED]")
    return clean


def _send_via_gmail_api(recipient, sender, subject, text_content, html_content=None):
    """
    Deliver email using the official Google Gmail REST API over HTTPS (port 443) with OAuth 2.0.
    Bypasses cloud provider SMTP restrictions.
    Does not log tokens or client secrets.
    Returns: (bool, str) -> (success, message_or_error)
    """
    import base64
    import socket
    from email.message import EmailMessage
    from django.conf import settings

    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '').strip() or os.environ.get('GOOGLE_CLIENT_ID', '').strip()
    client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '').strip() or os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
    refresh_token = getattr(settings, 'GOOGLE_REFRESH_TOKEN', '').strip() or os.environ.get('GOOGLE_REFRESH_TOKEN', '').strip()
    sender_email = (
        getattr(settings, 'GMAIL_SENDER_EMAIL', '').strip()
        or getattr(settings, 'DEFAULT_FROM_EMAIL', '').strip()
        or os.environ.get('GMAIL_SENDER_EMAIL', '').strip()
        or os.environ.get('DEFAULT_FROM_EMAIL', '').strip()
        or sender
        or "smartcampus.in.org@gmail.com"
    )

    secrets_to_mask = [client_id, client_secret, refresh_token]

    # Validate required credentials
    missing = []
    if not client_id:
        missing.append("GOOGLE_CLIENT_ID")
    if not client_secret:
        missing.append("GOOGLE_CLIENT_SECRET")
    if not refresh_token:
        missing.append("GOOGLE_REFRESH_TOKEN")

    if missing:
        err_msg = (
            f"Gmail API configuration incomplete: missing {', '.join(missing)}. "
            "Please configure these environment variables in Render (or authorize via /admin/gmail/oauth/init/) "
            "to enable Gmail API email delivery."
        )
        campus_email_logger.error("Gmail API missing configuration: %s", missing)
        return False, err_msg

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from google.auth.exceptions import RefreshError
        import googleapiclient.errors
    except ImportError as ie:
        err_msg = f"Google API client libraries are not installed ({ie}). Please ensure google-api-python-client is in requirements.txt."
        campus_email_logger.error("Gmail API import error: %s", err_msg)
        return False, err_msg

    try:
        # Build OAuth 2.0 Credentials with auto-refresh
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/gmail.send"],
        )

        # Build Gmail service resource (cache_discovery=False for clean serverless / ephemeral environments)
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)

        # Compose standard MIME email message
        message = EmailMessage()
        message.set_content(text_content or "")
        if html_content:
            message.add_alternative(html_content, subtype="html")

        # Set headers
        message["To"] = recipient
        message["From"] = sender_email
        message["Subject"] = subject

        raw_bytes = message.as_bytes()
        raw_b64 = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
        body = {"raw": raw_b64}

        campus_email_logger.info("Submitting email via Gmail API to %s from %s", recipient, sender_email)
        res = service.users().messages().send(userId="me", body=body).execute()

        msg_id = res.get("id", "")
        id_suffix = f" (Message ID: {msg_id})" if msg_id else ""
        campus_email_logger.info("Email accepted by Gmail API for %s%s", recipient, id_suffix)
        return True, f"Email accepted by Gmail API{id_suffix}."

    except RefreshError as rerr:
        raw_err = str(rerr)
        safe_err = _sanitize_error(raw_err, secrets_to_mask)
        err_msg = (
            "Gmail API authorization failed: The OAuth 2.0 refresh token is invalid, expired, or has been revoked. "
            f"Details: {safe_err}. Please re-authorize the application at /admin/gmail/oauth/init/ or generate a new GOOGLE_REFRESH_TOKEN."
        )
        campus_email_logger.error("Gmail API RefreshError for %s: %s", recipient, safe_err)
        return False, err_msg

    except googleapiclient.errors.HttpError as herr:
        raw_err = str(herr)
        safe_err = _sanitize_error(raw_err, secrets_to_mask)
        status_code = getattr(herr.resp, 'status', 0) if hasattr(herr, 'resp') else 0
        if status_code == 403:
            err_msg = f"Gmail API permission or quota error ({status_code}): {safe_err}. Check Google Cloud API permissions and daily sending quota."
        elif status_code == 400:
            err_msg = f"Gmail API bad request error ({status_code}): {safe_err}. Verify recipient email address."
        else:
            err_msg = f"Gmail API HTTP error ({status_code}): {safe_err}"
        campus_email_logger.error("Gmail API HttpError for %s: %s", recipient, safe_err)
        return False, err_msg

    except (socket.timeout, TimeoutError) as terr:
        err_msg = f"Gmail API connection timed out: {terr}. Transient network issue reaching Google APIs."
        campus_email_logger.warning("Gmail API timeout for %s: %s", recipient, err_msg)
        return False, err_msg

    except Exception as exc:
        raw_err = str(exc)
        safe_err = _sanitize_error(raw_err, secrets_to_mask)
        err_msg = f"Gmail API dispatch error: {safe_err}"
        campus_email_logger.error("Unexpected Gmail API error for %s: %s", recipient, safe_err)
        return False, err_msg


def _send_via_resend(recipient, sender, subject, text_content, html_content, resend_key):
    """
    Deliver email via Resend HTTPS API (port 443).
    Supports official Resend Python SDK with standard library urllib fallback.
    Never falls back to SMTP. Never logs secret keys or passwords.
    """
    import json
    import urllib.request
    import urllib.error
    from email.utils import parseaddr
    from django.conf import settings

    if not resend_key:
        campus_email_logger.error("Resend API key missing while Resend provider selected.")
        return False, "Resend API key is not configured. Please set the RESEND_API_KEY environment variable in Render."

    real_name, email_addr = parseaddr(sender)
    clean_addr = email_addr if email_addr else sender.strip()
    domain = clean_addr.split('@')[-1].lower() if '@' in clean_addr else ''

    if not domain:
        err_msg = "Invalid sender email address. Please configure DEFAULT_FROM_EMAIL in Render."
        campus_email_logger.error("Resend sender configuration error for %s: %s", recipient, err_msg)
        return False, f"Resend configuration error: {err_msg}"

    if domain in ["gmail.com", "googlemail.com"]:
        sender = "Smart Campus <onboarding@resend.dev>"
        domain = "resend.dev"

    try:
        import resend

        resend.api_key = resend_key
        params = {
            "from": sender,
            "to": [recipient],
            "subject": subject,
            "html": html_content or text_content,
        }
        if text_content:
            params["text"] = text_content

        campus_email_logger.info("Submitting email via Resend Python SDK to %s from %s", recipient, sender)
        response = resend.Emails.send(params)

        email_id = ""
        if isinstance(response, dict):
            email_id = response.get("id", "")
        elif hasattr(response, "id"):
            email_id = getattr(response, "id", "")

        id_suffix = f" (ID: {email_id})" if email_id else ""
        campus_email_logger.info("Email submitted successfully via Resend API to %s%s", recipient, id_suffix)
        return True, f"Email submitted successfully via Resend API{id_suffix}."

    except ImportError:
        try:
            campus_email_logger.info("Submitting email via Resend direct HTTPS API to %s from %s", recipient, sender)
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
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            timeout_val = int(getattr(settings, "EMAIL_TIMEOUT", None) or 15)
            with urllib.request.urlopen(req, timeout=timeout_val) as resp:
                resp_body = resp.read().decode("utf-8")
                resp_data = json.loads(resp_body) if resp_body else {}
                email_id = resp_data.get("id", "")
                id_suffix = f" (ID: {email_id})" if email_id else ""
                campus_email_logger.info("Email submitted successfully via Resend HTTPS API to %s%s", recipient, id_suffix)
                return True, f"Email submitted successfully via Resend API{id_suffix}."

        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", errors="ignore")
            safe_body = _sanitize_error(err_body, [resend_key])
            if "domain is not verified" in safe_body.lower() or "not verified" in safe_body.lower():
                safe_body = (
                    f"The sender domain '{domain}' is not verified in Resend. "
                    "Please verify your domain at https://resend.com/domains, or set DEFAULT_FROM_EMAIL "
                    "to 'Smart Campus <onboarding@resend.dev>' in your Render environment variables."
                )
            campus_email_logger.warning("Resend HTTPS API returned error %s for %s: %s", he.code, recipient, safe_body)
            return False, f"Resend API error ({he.code}): {safe_body}"
        except urllib.error.URLError as ue:
            safe_err = _sanitize_error(str(ue.reason), [resend_key])
            campus_email_logger.warning("Resend network error for %s: %s", recipient, safe_err)
            return False, f"Resend network connection error: {safe_err}"
        except Exception as exc:
            safe_err = _sanitize_error(str(exc), [resend_key])
            campus_email_logger.warning("Resend exception for %s: %s", recipient, safe_err)
            return False, f"Resend API error: {safe_err}"

    except Exception as exc:
        raw_msg = str(exc)
        safe_msg = _sanitize_error(raw_msg, [resend_key])
        if "domain is not verified" in safe_msg.lower() or "not verified" in safe_msg.lower():
            safe_msg = (
                f"The sender domain '{domain}' is not verified in Resend. "
                "Please verify your domain at https://resend.com/domains, or set DEFAULT_FROM_EMAIL "
                "to 'Smart Campus <onboarding@resend.dev>' in your Render environment variables."
            )
        campus_email_logger.warning("Resend SDK error for %s: %s", recipient, safe_msg)
        return False, f"Resend API error: {safe_msg}"


def _send_via_smtp(recipient, sender, subject, text_content, html_content):
    """
    Standard Django SMTP backend with explicit finite timeout guard.
    Used only when EMAIL_PROVIDER is explicitly set to 'smtp'.
    """
    import socket
    import smtplib
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives, get_connection

    timeout_val = int(getattr(settings, 'EMAIL_TIMEOUT', None) or 15)
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


def send_campus_email(to_email, subject, text_content, html_content=None, from_email=None):
    """
    Robust central dispatcher for sending email across Smart Campus.
    Primary Strategy: Official Google Gmail REST API over HTTPS (OAuth 2.0).
    Never silently falls back to SMTP if Gmail API fails.
    Returns: (bool, str) -> (success, message_or_error)
    """
    import os
    from django.conf import settings

    recipient = to_email.strip() if isinstance(to_email, str) else str(to_email)
    if not recipient:
        return False, "Recipient email address is missing."

    provider = (
        getattr(settings, 'EMAIL_PROVIDER', '').strip().lower()
        or os.environ.get('EMAIL_PROVIDER', '').strip().lower()
    )
    if not provider:
        provider = "gmail_api"

    # Strategy 1: Official Gmail API (Primary)
    if provider in ["gmail_api", "gmail", "google"]:
        sender = (
            from_email
            or getattr(settings, 'GMAIL_SENDER_EMAIL', None)
            or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
            or "smartcampus.in.org@gmail.com"
        )
        return _send_via_gmail_api(
            recipient=recipient,
            sender=sender,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
        )

    # Strategy 2: Resend HTTPS API (Alternative)
    if provider == "resend":
        resend_key = getattr(settings, 'RESEND_API_KEY', '').strip() or os.environ.get('RESEND_API_KEY', '').strip()
        sender = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', None) or "Smart Campus <onboarding@resend.dev>"
        return _send_via_resend(
            recipient=recipient,
            sender=sender,
            subject=subject,
            text_content=text_content,
            html_content=html_content,
            resend_key=resend_key,
        )

    # Strategy 3: Standard SMTP (used only when EMAIL_PROVIDER is explicitly set to 'smtp')
    sender = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None) or "smartcampus.in.org@gmail.com"
    return _send_via_smtp(
        recipient=recipient,
        sender=sender,
        subject=subject,
        text_content=text_content,
        html_content=html_content,
    )


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
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)

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
