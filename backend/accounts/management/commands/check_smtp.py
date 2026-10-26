import os
import socket
import smtplib
import time
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Diagnose SMTP connectivity and credentials step-by-step without exposing secret keys."

    def add_arguments(self, parser):
        parser.add_argument(
            "--to",
            dest="to_email",
            help="Optional test recipient email to send a verification message to.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== SMART CAMPUS EMAIL DIAGNOSTICS ==="))

        host = getattr(settings, "EMAIL_HOST", "smtp.gmail.com")
        port = int(getattr(settings, "EMAIL_PORT", 587) or 587)
        timeout = int(getattr(settings, "EMAIL_TIMEOUT", None) or 10)
        use_tls = getattr(settings, "EMAIL_USE_TLS", True)
        use_ssl = getattr(settings, "EMAIL_USE_SSL", False)
        user = getattr(settings, "EMAIL_HOST_USER", "")
        password = getattr(settings, "EMAIL_HOST_PASSWORD", "")
        resend_key = getattr(settings, "RESEND_API_KEY", "") or os.environ.get("RESEND_API_KEY", "")

        # 1. Environment & Config Summary
        self.stdout.write("\n[1/5] Configuration Inspection:")
        self.stdout.write(f"  EMAIL_HOST         : {host}")
        self.stdout.write(f"  EMAIL_PORT         : {port}")
        self.stdout.write(f"  EMAIL_TIMEOUT      : {timeout} seconds")
        self.stdout.write(f"  EMAIL_USE_TLS      : {use_tls}")
        self.stdout.write(f"  EMAIL_USE_SSL      : {use_ssl}")
        self.stdout.write(f"  EMAIL_HOST_USER    : {user or '(empty)'}")
        self.stdout.write(f"  EMAIL_HOST_PASSWORD: {'[Configured - ' + str(len(password)) + ' chars]' if password else '[MISSING / EMPTY]'}")
        self.stdout.write(f"  RESEND_API_KEY     : {'[Configured - ' + str(len(resend_key)) + ' chars]' if resend_key else '[Not Configured]'}")

        # 2. DNS Resolution
        self.stdout.write("\n[2/5] DNS Resolution Check:")
        t0 = time.time()
        try:
            infos = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
            elapsed = (time.time() - t0) * 1000
            ips = sorted(list({i[4][0] for i in infos}))
            self.stdout.write(self.style.SUCCESS(f"  OK: Resolved {host} to {ips[:3]} in {elapsed:.1f}ms"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  FAILED: Could not resolve {host}: {e}"))
            return

        # 3. Raw TCP Connectivity
        self.stdout.write(f"\n[3/5] TCP Connect to {host}:{port} (timeout={timeout}s):")
        t0 = time.time()
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            elapsed = (time.time() - t0) * 1000
            sock.close()
            self.stdout.write(self.style.SUCCESS(f"  OK: Connected to {host}:{port} in {elapsed:.1f}ms"))
        except (socket.timeout, TimeoutError):
            self.stdout.write(self.style.ERROR(f"  FAILED: Connection timed out after {timeout}s."))
            self.stdout.write(self.style.WARNING("  -> Outbound TCP traffic to port " + str(port) + " appears blocked or dropped by cloud egress."))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  FAILED: Could not connect: {e}"))
            return

        # 4. SMTP Handshake & STARTTLS
        self.stdout.write("\n[4/5] SMTP Handshake & Security Negotiation:")
        smtp = None
        try:
            if use_ssl:
                smtp = smtplib.SMTP_SSL(host, port, timeout=timeout)
                smtp.ehlo()
                self.stdout.write(self.style.SUCCESS("  OK: Connected using SSL."))
            else:
                smtp = smtplib.SMTP(host, port, timeout=timeout)
                smtp.ehlo()
                if use_tls:
                    smtp.starttls()
                    smtp.ehlo()
                    self.stdout.write(self.style.SUCCESS("  OK: STARTTLS negotiation successful."))
                else:
                    self.stdout.write(self.style.WARNING("  NOTICE: TLS disabled."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  FAILED: SMTP Handshake error: {e}"))
            if smtp:
                try:
                    smtp.close()
                except Exception:
                    pass
            return

        # 5. SMTP Authentication
        self.stdout.write("\n[5/5] SMTP Authentication:")
        if not user or not password:
            self.stdout.write(self.style.WARNING("  SKIPPED: EMAIL_HOST_USER or EMAIL_HOST_PASSWORD is not set."))
            smtp.close()
            return

        try:
            smtp.login(user, password)
            self.stdout.write(self.style.SUCCESS(f"  OK: Successfully authenticated as {user}!"))
        except smtplib.SMTPAuthenticationError as auth_err:
            self.stdout.write(self.style.ERROR(f"  FAILED: Authentication rejected by {host}."))
            self.stdout.write(self.style.WARNING(f"  -> Details: {auth_err}"))
            self.stdout.write(self.style.NOTICE("  -> If using Gmail, ensure 2FA is enabled and you are using a 16-character App Password (not your account password)."))
            smtp.close()
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  FAILED: Unexpected login error: {e}"))
            smtp.close()
            return

        # Optional Send
        to_email = options.get("to_email")
        if to_email:
            self.stdout.write(f"\n[+] Sending test email to {to_email}...")
            try:
                msg = f"Subject: Smart Campus Test\n\nThis is a diagnostic email from Smart Campus."
                smtp.sendmail(user, [to_email], msg)
                self.stdout.write(self.style.SUCCESS(f"  OK: Test email sent to {to_email}!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  FAILED to send message: {e}"))

        try:
            smtp.quit()
        except Exception:
            pass

        self.stdout.write(self.style.SUCCESS("\n=== DIAGNOSTICS COMPLETED SUCCESSFULLY ==="))
