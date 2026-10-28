import os
import urllib.parse
import urllib.request
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.services import send_campus_email, _sanitize_error


class Command(BaseCommand):
    help = "Authorize Gmail API OAuth 2.0 and generate GOOGLE_REFRESH_TOKEN for Render deployment."

    def add_arguments(self, parser):
        parser.add_argument(
            "--client-id",
            dest="client_id",
            help="Google OAuth Client ID (optional if set in environment)",
        )
        parser.add_argument(
            "--client-secret",
            dest="client_secret",
            help="Google OAuth Client Secret (optional if set in environment)",
        )
        parser.add_argument(
            "--redirect-uri",
            dest="redirect_uri",
            help="OAuth Redirect URI matching Google Cloud Console exactly",
        )
        parser.add_argument(
            "--test-send",
            dest="test_recipient",
            help="Send a verification email to this recipient using configured Gmail API",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== GMAIL API OAUTH 2.0 SETUP & DIAGNOSTICS ==="))

        test_recipient = options.get("test_recipient")
        if test_recipient:
            self.stdout.write(f"\n[+] Sending test email via Gmail API to {test_recipient}...")
            ok, msg = send_campus_email(
                to_email=test_recipient,
                subject="Smart Campus - Gmail API Live Test",
                text_content="This is a verified test email sent via the official Google Gmail REST API over HTTPS port 443.",
            )
            if ok:
                self.stdout.write(self.style.SUCCESS(f"  OK: {msg}"))
            else:
                self.stdout.write(self.style.ERROR(f"  FAILED: {msg}"))
            return

        client_id = (
            options.get("client_id")
            or getattr(settings, "GOOGLE_CLIENT_ID", "").strip()
            or os.environ.get("GOOGLE_CLIENT_ID", "").strip()
        )
        client_secret = (
            options.get("client_secret")
            or getattr(settings, "GOOGLE_CLIENT_SECRET", "").strip()
            or os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
        )
        site_url = getattr(settings, "SITE_URL", "https://ai-college-campus-management.onrender.com").rstrip("/")
        default_redirect_uri = f"{site_url}/admin/gmail/oauth/callback/"
        redirect_uri = options.get("redirect_uri") or default_redirect_uri

        self.stdout.write("\n[1/3] Checking Credentials:")
        self.stdout.write(f"  GOOGLE_CLIENT_ID     : {'[Configured - ' + str(len(client_id)) + ' chars]' if client_id else self.style.ERROR('[MISSING]')}")
        self.stdout.write(f"  GOOGLE_CLIENT_SECRET : {'[Configured - ' + str(len(client_secret)) + ' chars]' if client_secret else self.style.ERROR('[MISSING]')}")
        self.stdout.write(f"  Redirect URI         : {redirect_uri}")

        if not client_id or not client_secret:
            self.stdout.write(self.style.ERROR("\nERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are required."))
            self.stdout.write("Pass them via environment variables or CLI arguments: --client-id and --client-secret\n")
            return

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/gmail.send",
            "access_type": "offline",
            "prompt": "consent",
        }
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

        self.stdout.write("\n[2/3] Authorization Steps:")
        self.stdout.write("  1. In Google Cloud Console, ensure this Redirect URI is added under 'Authorized redirect URIs':")
        self.stdout.write(self.style.WARNING(f"     {redirect_uri}"))
        self.stdout.write("  2. Open the following URL in your web browser:")
        self.stdout.write(self.style.NOTICE(f"\n{auth_url}\n"))
        self.stdout.write("  3. Log in with your Gmail sender account, grant permission, and Google will redirect you.")

        self.stdout.write("\n[3/3] Exchange Code for Refresh Token:")
        self.stdout.write("  After approving, copy either:")
        self.stdout.write("  - The 'code' query parameter value from your browser address bar, OR")
        self.stdout.write("  - The complete redirect URL (e.g. https://.../callback/?code=4/0A...)")

        try:
            user_input = input("\nEnter the authorization code or full redirect URL: ").strip()
        except (KeyboardInterrupt, EOFError):
            self.stdout.write("\nAborted.")
            return

        if not user_input:
            self.stdout.write(self.style.ERROR("No code provided. Aborting."))
            return

        code = user_input
        if "code=" in user_input:
            try:
                parsed = urllib.parse.urlparse(user_input)
                qs = urllib.parse.parse_qs(parsed.query)
                code = qs.get("code", [user_input])[0]
            except Exception:
                code = user_input

        token_payload = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        self.stdout.write("\n[+] Exchanging code with https://oauth2.googleapis.com/token...")
        try:
            req = urllib.request.Request(
                "https://oauth2.googleapis.com/token",
                data=urllib.parse.urlencode(token_payload).encode("utf-8"),
                headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "SmartCampus/1.0"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                token_data = json.loads(resp.read().decode("utf-8"))

            refresh_token = token_data.get("refresh_token")
            if not refresh_token:
                self.stdout.write(self.style.WARNING("WARNING: Google did not return a refresh token (token was already authorized)."))
                self.stdout.write("To force Google to return a new refresh token, re-run with prompt=consent or revoke access in your Google Account security settings.")
                return

            self.stdout.write(self.style.SUCCESS("\n=== AUTHORIZATION SUCCESSFUL! ==="))
            self.stdout.write("\nAdd this line to your Render Environment Variables:")
            self.stdout.write(self.style.SUCCESS(f"GOOGLE_REFRESH_TOKEN={refresh_token}"))
            self.stdout.write(f"EMAIL_PROVIDER=gmail_api")
            self.stdout.write(f"GMAIL_SENDER_EMAIL=smartcampus.in.org@gmail.com")
            self.stdout.write(self.style.SUCCESS("\n=== SETUP COMPLETE ==="))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to exchange code: {e}"))
