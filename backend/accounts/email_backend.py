import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

campus_logger = logging.getLogger("campus_email")


class CampusEmailBackend(BaseEmailBackend):
    """
    Custom Django Email Backend that dispatches all Django emails (including PasswordResetForm)
    through the official Google Gmail REST API over HTTPS (Port 443).
    Ensures safe, non-blocking delivery on cloud hosting environments (Render).
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        from accounts.services import send_campus_email

        num_sent = 0
        for message in email_messages:
            try:
                recipients = message.to or []
                if not recipients:
                    continue

                subject = message.subject or "Smart Campus Notification"
                text_content = message.body or ""
                html_content = None

                # Extract HTML alternative if present
                if hasattr(message, "alternatives"):
                    for content, mimetype in message.alternatives:
                        if mimetype == "text/html":
                            html_content = content
                            break
                if not html_content and getattr(message, "content_subtype", "") == "html":
                    html_content = message.body

                from_email = getattr(message, "from_email", None) or getattr(settings, "DEFAULT_FROM_EMAIL", None)

                all_succeeded = True
                last_error = ""

                for recipient in recipients:
                    success, msg = send_campus_email(
                        to_email=recipient,
                        subject=subject,
                        text_content=text_content,
                        html_content=html_content,
                        from_email=from_email,
                    )
                    if not success:
                        all_succeeded = False
                        last_error = msg
                        campus_logger.warning("CampusEmailBackend failed delivering to %s: %s", recipient, msg)

                if all_succeeded:
                    num_sent += 1
                elif not self.fail_silently:
                    raise Exception(last_error or "Failed to deliver email through campus email dispatcher.")

            except Exception as exc:
                campus_logger.error("CampusEmailBackend exception during send_messages: %s", str(exc))
                if not self.fail_silently:
                    raise

        return num_sent
