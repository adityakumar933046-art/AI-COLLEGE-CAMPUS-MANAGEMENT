import os
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from google.auth.exceptions import RefreshError
import googleapiclient.errors

from accounts.services import (
    send_campus_email,
    send_account_credentials_email,
    send_student_credentials_email,
    _sanitize_error,
)
from students.models import StudentProfile
from students.services import create_student

User = get_user_model()


class GmailApiEmailIntegrationTests(TestCase):
    """
    Comprehensive test suite for Gmail API OAuth 2.0 integration,
    mocked token refresh, error handling, secret sanitization,
    student creation preservation, and credential resending.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_admin_user",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role="ADMIN",
        )

    # -------------------------------------------------------------
    # 1. Successful Gmail API sending
    # -------------------------------------------------------------
    @override_settings(
        EMAIL_PROVIDER="gmail_api",
        GOOGLE_CLIENT_ID="mock_client_id_12345",
        GOOGLE_CLIENT_SECRET="mock_client_secret_67890",
        GOOGLE_REFRESH_TOKEN="mock_refresh_token_abcde",
        GMAIL_SENDER_EMAIL="smartcampus.in.org@gmail.com",
    )
    def test_gmail_api_successful_sending(self):
        mock_service = MagicMock()
        mock_messages = MagicMock()
        mock_send = MagicMock()
        mock_send.execute.return_value = {"id": "gmail_msg_18a1b2c3d4e5f6"}
        mock_messages.send.return_value = mock_send
        mock_service.users.return_value.messages.return_value = mock_messages

        with patch("accounts.services.build", return_value=mock_service, create=True) as mock_build:
            with patch("googleapiclient.discovery.build", return_value=mock_service):
                ok, msg = send_campus_email(
                    to_email="student@example.com",
                    subject="Your Smart Campus Credentials",
                    text_content="Welcome to Smart Campus. Username: student123",
                    html_content="<p>Welcome to Smart Campus. Username: student123</p>",
                )
                self.assertTrue(ok)
                self.assertIn("Email accepted by Gmail API", msg)
                self.assertIn("gmail_msg_18a1b2c3d4e5f6", msg)
                mock_messages.send.assert_called_once()
                call_kwargs = mock_messages.send.call_args[1]
                self.assertEqual(call_kwargs["userId"], "me")
                self.assertIn("raw", call_kwargs["body"])

    # -------------------------------------------------------------
    # 2. Missing Configuration Handling
    # -------------------------------------------------------------
    @override_settings(
        EMAIL_PROVIDER="gmail_api",
        GOOGLE_CLIENT_ID="",
        GOOGLE_CLIENT_SECRET="",
        GOOGLE_REFRESH_TOKEN="",
    )
    def test_gmail_api_missing_configuration_handled_clearly(self):
        with patch.dict(os.environ, {
            "GOOGLE_CLIENT_ID": "",
            "GOOGLE_CLIENT_SECRET": "",
            "GOOGLE_REFRESH_TOKEN": "",
        }):
            ok, msg = send_campus_email(
                to_email="student@example.com",
                subject="Test Subject",
                text_content="Content",
            )
            self.assertFalse(ok)
            self.assertIn("Gmail API configuration incomplete", msg)
            self.assertIn("GOOGLE_CLIENT_ID", msg)
            self.assertIn("GOOGLE_CLIENT_SECRET", msg)
            self.assertIn("GOOGLE_REFRESH_TOKEN", msg)

    # -------------------------------------------------------------
    # 3. Revoked or Expired Refresh Token (RefreshError)
    # -------------------------------------------------------------
    @override_settings(
        EMAIL_PROVIDER="gmail_api",
        GOOGLE_CLIENT_ID="mock_client_id_12345",
        GOOGLE_CLIENT_SECRET="mock_client_secret_67890",
        GOOGLE_REFRESH_TOKEN="mock_revoked_token_abcde",
        GMAIL_SENDER_EMAIL="smartcampus.in.org@gmail.com",
    )
    def test_gmail_api_revoked_or_expired_token(self):
        with patch("googleapiclient.discovery.build", side_effect=RefreshError("invalid_grant: Token has been expired or revoked.")):
            ok, msg = send_campus_email(
                to_email="student@example.com",
                subject="Test Subject",
                text_content="Content",
            )
            self.assertFalse(ok)
            self.assertIn("Gmail API authorization failed", msg)
            self.assertIn("invalid, expired, or has been revoked", msg)

    # -------------------------------------------------------------
    # 4. Gmail API HttpError (Quota / Permission 403)
    # -------------------------------------------------------------
    @override_settings(
        EMAIL_PROVIDER="gmail_api",
        GOOGLE_CLIENT_ID="mock_client_id_12345",
        GOOGLE_CLIENT_SECRET="mock_client_secret_67890",
        GOOGLE_REFRESH_TOKEN="mock_refresh_token_abcde",
        GMAIL_SENDER_EMAIL="smartcampus.in.org@gmail.com",
    )
    def test_gmail_api_http_error_quota_or_rate_limit(self):
        mock_resp = MagicMock()
        mock_resp.status = 403
        mock_resp.reason = "Forbidden"
        http_err = googleapiclient.errors.HttpError(resp=mock_resp, content=b"Daily sending quota exceeded")

        mock_service = MagicMock()
        mock_messages = MagicMock()
        mock_send = MagicMock()
        mock_send.execute.side_effect = http_err
        mock_messages.send.return_value = mock_send
        mock_service.users.return_value.messages.return_value = mock_messages

        with patch("googleapiclient.discovery.build", return_value=mock_service):
            ok, msg = send_campus_email(
                to_email="student@example.com",
                subject="Test Subject",
                text_content="Content",
            )
            self.assertFalse(ok)
            self.assertIn("permission or quota error (403)", msg)

    # -------------------------------------------------------------
    # 5. Network Timeout Handling
    # -------------------------------------------------------------
    @override_settings(
        EMAIL_PROVIDER="gmail_api",
        GOOGLE_CLIENT_ID="mock_client_id_12345",
        GOOGLE_CLIENT_SECRET="mock_client_secret_67890",
        GOOGLE_REFRESH_TOKEN="mock_refresh_token_abcde",
        GMAIL_SENDER_EMAIL="smartcampus.in.org@gmail.com",
    )
    def test_gmail_api_timeout_handling(self):
        with patch("googleapiclient.discovery.build", side_effect=TimeoutError("The read operation timed out")):
            ok, msg = send_campus_email(
                to_email="student@example.com",
                subject="Test Subject",
                text_content="Content",
            )
            self.assertFalse(ok)
            self.assertIn("connection timed out", msg.lower())

    # -------------------------------------------------------------
    # 6. Student Creation Works Even When Email Sending Fails
    # -------------------------------------------------------------
    def test_student_creation_succeeds_even_when_email_fails(self):
        student_data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice_test@example.com",
            "admission_no": "ADM2026GMAIL01",
            "roll_no": "CS201",
            "semester": 1,
            "section": "A",
            "phone": "9876543210",
            "status": "ACTIVE",
        }
        result = create_student(data=student_data, created_by=self.user)
        self.assertTrue(result["success"], f"Failed with errors: {result.get('errors')}")
        new_user = result["user"]
        temp_pwd = result["password"]

        # Simulate Gmail API failure during sending
        with patch("accounts.services.send_campus_email", return_value=(False, "Gmail API dispatch error: simulated failure")):
            email_ok, email_err = send_student_credentials_email(new_user, temp_pwd)
            self.assertFalse(email_ok)
            self.assertIn("Gmail API dispatch error", email_err)

        # Confirm student user and profile remain safely in database
        self.assertTrue(User.objects.filter(email="alice_test@example.com").exists())
        self.assertTrue(StudentProfile.objects.filter(user=new_user).exists())

    # -------------------------------------------------------------
    # 7. Resending Credentials Does Not Create Duplicate Accounts
    # -------------------------------------------------------------
    def test_resending_credentials_does_not_duplicate_accounts(self):
        student_data = {
            "first_name": "Bob",
            "last_name": "Jones",
            "email": "bob_test@example.com",
            "admission_no": "ADM2026GMAIL02",
            "roll_no": "CS202",
            "semester": 1,
            "section": "A",
            "phone": "9876543211",
        }
        res = create_student(data=student_data, created_by=self.user)
        self.assertTrue(res["success"], f"Failed with errors: {res.get('errors')}")
        bob_user = res["user"]
        initial_user_count = User.objects.count()
        initial_student_count = StudentProfile.objects.count()

        # Simulate resend workflow: change password and send email via Gmail API
        bob_user.set_password("NewSecureTempPass999!")
        bob_user.save()

        with patch("accounts.services.send_campus_email", return_value=(True, "Email accepted by Gmail API")):
            ok, _ = send_account_credentials_email(bob_user, "NewSecureTempPass999!", role="STUDENT")
            self.assertTrue(ok)

        # User and StudentProfile counts must remain identical (no duplicate records)
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertEqual(StudentProfile.objects.count(), initial_student_count)

    # -------------------------------------------------------------
    # 8. Secret Redaction Helper
    # -------------------------------------------------------------
    def test_sanitization_helper_redacts_google_secrets(self):
        raw_error = "Error with client secret 12345SECRET and refresh token 1//04REFRESH_TOKEN and password TempPass123"
        sanitized = _sanitize_error(raw_error, ["12345SECRET", "1//04REFRESH_TOKEN", "TempPass123"])
        self.assertNotIn("12345SECRET", sanitized)
        self.assertNotIn("1//04REFRESH_TOKEN", sanitized)
        self.assertNotIn("TempPass123", sanitized)
        self.assertIn("[REDACTED]", sanitized)

    # -------------------------------------------------------------
    # 9. Existing Email Templates and Credential Content Integrity
    # -------------------------------------------------------------
    def test_email_template_rendering_integrity(self):
        context = {
            "name": "Jane Doe",
            "username": "janedoe",
            "temporary_password": "TempPassword999",
            "role_display": "Student",
            "login_url": "https://ai-college-campus-management.onrender.com/login/",
        }
        text_content = render_to_string("emails/account_credentials.txt", context)
        html_content = render_to_string("emails/account_credentials.html", context)

        self.assertIn("Jane Doe", text_content)
        self.assertIn("janedoe", text_content)
        self.assertIn("TempPassword999", text_content)
        self.assertIn("https://ai-college-campus-management.onrender.com/login/", text_content)

        self.assertIn("Jane Doe", html_content)
        self.assertIn("janedoe", html_content)
        self.assertIn("TempPassword999", html_content)
        self.assertIn("https://ai-college-campus-management.onrender.com/login/", html_content)


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse


class PasswordResetWorkflowTests(TestCase):
    """
    Automated test suite verifying the complete Password Reset workflow:
    - Forgot-password page & loading overlay rendering
    - Gmail API dispatch via CampusEmailBackend
    - Unknown email handling
    - Valid and invalid token verification
    - Secure password update in the database
    - Success screen & Back to Login navigation
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="student_alice",
            email="alice@student.smartcampus.edu",
            password="OriginalPassword123!",
            first_name="Alice",
            last_name="Smith",
            role="STUDENT",
        )

    def test_password_reset_page_renders_loading_and_back_button(self):
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Forgot Password?")
        self.assertContains(response, "loadingOverlay")
        self.assertContains(response, "Sending password reset email...")
        self.assertContains(response, "Back to Login")

    def test_forgot_password_alias_redirects_to_password_reset(self):
        response = self.client.get(reverse("forgot_password"))
        self.assertRedirects(response, reverse("password_reset"))

    @override_settings(
        EMAIL_BACKEND="accounts.email_backend.CampusEmailBackend",
        SITE_URL="https://ai-college-campus-management.onrender.com",
    )
    @patch("accounts.services.send_campus_email")
    def test_valid_password_reset_dispatches_email_with_production_url(self, mock_send):
        mock_send.return_value = (True, "Email accepted by Gmail API")

        response = self.client.post(
            reverse("password_reset"),
            {"email": "alice@student.smartcampus.edu"},
        )
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertTrue(mock_send.called)

        # Inspect email dispatch arguments
        kwargs = mock_send.call_args.kwargs
        self.assertEqual(kwargs.get("to_email"), "alice@student.smartcampus.edu")
        self.assertIn("Password Reset", kwargs.get("subject", ""))
        self.assertIn("https://ai-college-campus-management.onrender.com", kwargs.get("text_content", ""))
        self.assertIn("/reset/", kwargs.get("text_content", ""))

    @override_settings(EMAIL_BACKEND="accounts.email_backend.CampusEmailBackend")
    @patch("accounts.services.send_campus_email")
    def test_unknown_email_does_not_reveal_user_absence(self, mock_send):
        response = self.client.post(
            reverse("password_reset"),
            {"email": "nonexistent@example.com"},
        )
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertFalse(mock_send.called)

    def test_password_reset_confirm_with_valid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        confirm_url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        # Django redirects from /reset/<uid>/<token>/ to /reset/<uid>/set-password/ to mask token
        response = self.client.get(confirm_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create New Password")

        # Submit new password to set-password route
        set_pwd_url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": "set-password"})
        post_response = self.client.post(
            set_pwd_url,
            {
                "new_password1": "NewSecureCampusPass456!",
                "new_password2": "NewSecureCampusPass456!",
            },
        )
        self.assertRedirects(post_response, reverse("password_reset_complete"))

        # Verify password successfully updated in database
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecureCampusPass456!"))
        self.assertFalse(self.user.check_password("OriginalPassword123!"))

    def test_password_reset_confirm_with_invalid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        invalid_token = "invalid-token-12345"

        confirm_url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": invalid_token})
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password Reset Link Invalid")
        self.assertContains(response, "Request New Reset Link")
        self.assertContains(response, "Back to Login")

    def test_password_reset_confirm_mismatched_passwords(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        confirm_url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        # Initialize session token
        self.client.get(confirm_url)

        set_pwd_url = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": "set-password"})
        response = self.client.post(
            set_pwd_url,
            {
                "new_password1": "NewPassword123!",
                "new_password2": "MismatchedPassword456!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("match", response.content.decode("utf-8").lower())
        # Password remains unchanged in DB
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("OriginalPassword123!"))

    def test_password_reset_complete_renders_success_and_back_to_login(self):
        response = self.client.get(reverse("password_reset_complete"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password Reset Successful")
        self.assertContains(response, "Your password has been updated successfully.")
        self.assertContains(response, "Back to Login")
        self.assertContains(response, reverse("login"))
