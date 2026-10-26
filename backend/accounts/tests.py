import os
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from accounts.services import (
    send_campus_email,
    send_account_credentials_email,
    send_student_credentials_email,
    _sanitize_error,
)
from students.models import StudentProfile
from students.services import create_student

User = get_user_model()


class ResendEmailIntegrationTests(TestCase):
    """
    Test suite for Resend email integration, error handling,
    secret redaction, template rendering, and student account safety.
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
    # 1. Successful Resend API response handled correctly
    # -------------------------------------------------------------
    @override_settings(EMAIL_PROVIDER="resend", RESEND_API_KEY="re_test_dummy_key_12345")
    def test_resend_api_success_handling(self):
        mock_response = {"id": "resend_msg_test_abc123"}
        with patch("resend.Emails.send", return_value=mock_response) as mock_send:
            ok, msg = send_campus_email(
                to_email="test@example.com",
                subject="Test Subject",
                text_content="Plain text content",
                html_content="<p>HTML content</p>",
            )
            self.assertTrue(ok)
            self.assertIn("resend_msg_test_abc123", msg)
            self.assertIn("Email submitted successfully", msg)
            mock_send.assert_called_once()
            call_params = mock_send.call_args[0][0]
            self.assertEqual(call_params["to"], ["test@example.com"])
            self.assertEqual(call_params["subject"], "Test Subject")

    # -------------------------------------------------------------
    # 2. Resend API error produces a safe failure result
    # -------------------------------------------------------------
    @override_settings(EMAIL_PROVIDER="resend", RESEND_API_KEY="re_test_dummy_key_12345")
    def test_resend_api_error_produces_safe_failure(self):
        with patch("resend.Emails.send", side_effect=Exception("Domain not verified: example.com")):
            ok, msg = send_campus_email(
                to_email="test@example.com",
                subject="Test Subject",
                text_content="Plain text content",
            )
            self.assertFalse(ok)
            self.assertIn("Resend API error", msg)
            self.assertIn("Domain not verified", msg)

    # -------------------------------------------------------------
    # 3. Missing RESEND_API_KEY handled clearly
    # -------------------------------------------------------------
    @override_settings(EMAIL_PROVIDER="resend", RESEND_API_KEY="")
    def test_missing_resend_api_key_handled_clearly(self):
        with patch.dict(os.environ, {"RESEND_API_KEY": ""}):
            ok, msg = send_campus_email(
                to_email="test@example.com",
                subject="Test Subject",
                text_content="Plain text content",
            )
            self.assertFalse(ok)
            self.assertIn("Resend API key is not configured", msg)

    # -------------------------------------------------------------
    # 4. Student creation still works when email sending fails
    # -------------------------------------------------------------
    def test_student_creation_succeeds_even_when_email_fails(self):
        student_data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "admission_no": "ADM2026001",
            "roll_no": "CS101",
            "semester": 1,
            "section": "A",
            "phone": "9876543210",
            "status": "ACTIVE",
        }
        result = create_student(data=student_data, created_by=self.user)
        self.assertTrue(result["success"], f"Failed with errors: {result.get('errors')}")
        new_user = result["user"]
        temp_pwd = result["password"]

        # Simulate email failure
        with patch("accounts.services.send_campus_email", return_value=(False, "Resend API error: timeout")):
            email_ok, email_err = send_student_credentials_email(new_user, temp_pwd)
            self.assertFalse(email_ok)

        # Confirm student user and profile exist in database
        self.assertTrue(User.objects.filter(email="alice@example.com").exists())
        self.assertTrue(StudentProfile.objects.filter(user=new_user).exists())

    # -------------------------------------------------------------
    # 5. Resending credentials does not create duplicate accounts
    # -------------------------------------------------------------
    def test_resending_credentials_does_not_duplicate_accounts(self):
        student_data = {
            "first_name": "Bob",
            "last_name": "Jones",
            "email": "bob@example.com",
            "admission_no": "ADM2026002",
            "roll_no": "CS102",
            "semester": 1,
            "section": "A",
            "phone": "9876543211",
        }
        res = create_student(data=student_data, created_by=self.user)
        self.assertTrue(res["success"], f"Failed with errors: {res.get('errors')}")
        bob_user = res["user"]
        initial_user_count = User.objects.count()
        initial_student_count = StudentProfile.objects.count()

        # Simulate resend workflow: change password and send email
        bob_user.set_password("NewTempPass123!")
        bob_user.save()

        with patch("accounts.services.send_account_credentials_email", return_value=(True, "Email submitted")):
            ok, _ = send_account_credentials_email(bob_user, "NewTempPass123!", role="STUDENT")
            self.assertTrue(ok)

        # User and StudentProfile counts must remain identical (no duplicate records)
        self.assertEqual(User.objects.count(), initial_user_count)
        self.assertEqual(StudentProfile.objects.count(), initial_student_count)

    # -------------------------------------------------------------
    # 6. No plaintext password or API key is exposed/written
    # -------------------------------------------------------------
    def test_sanitization_helper_redacts_secrets(self):
        raw_error = "Failed to connect with secret re_live_abcdef123456789 and password SuperSecret123"
        sanitized = _sanitize_error(raw_error, ["re_live_abcdef123456789", "SuperSecret123"])
        self.assertNotIn("re_live_abcdef123456789", sanitized)
        self.assertNotIn("SuperSecret123", sanitized)
        self.assertIn("[REDACTED]", sanitized)

    # -------------------------------------------------------------
    # 7. Existing email templates and credential content remain intact
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
