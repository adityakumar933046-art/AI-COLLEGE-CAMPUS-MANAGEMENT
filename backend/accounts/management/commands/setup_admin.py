"""
Create an admin user from environment variables (for platforms without shell access).
Reads: CAMPUS_ADMIN_USERNAME, CAMPUS_ADMIN_EMAIL, CAMPUS_ADMIN_PASSWORD
Remove CAMPUS_ADMIN_PASSWORD from environment after first successful deploy.
"""
import os

from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Create a campus admin from environment variables (one-time setup)."

    def handle(self, *args, **options):
        username = os.environ.get("CAMPUS_ADMIN_USERNAME", "").strip()
        email = os.environ.get("CAMPUS_ADMIN_EMAIL", "").strip()
        password = os.environ.get("CAMPUS_ADMIN_PASSWORD", "").strip()

        if not username or not password:
            self.stdout.write("[setup_admin] CAMPUS_ADMIN_USERNAME or CAMPUS_ADMIN_PASSWORD not set. Skipping.")
            return

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            changed = False
            if user.role != "ADMIN":
                user.role = "ADMIN"
                changed = True
            if not user.is_staff:
                user.is_staff = True
                changed = True
            if not user.is_superuser:
                user.is_superuser = True
                changed = True
            if not user.is_active:
                user.is_active = True
                changed = True
            if changed:
                user.save()
                self.stdout.write(self.style.WARNING(f"[setup_admin] User '{username}' existed — updated role to ADMIN."))
            else:
                self.stdout.write(f"[setup_admin] User '{username}' already exists with role=ADMIN. Skipping.")
            return

        user = User(
            username=username,
            email=email or f"{username}@campus.local",
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_active_account=True,
            must_change_password=False,
        )
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"[setup_admin] Admin user '{username}' created successfully."))
        self.stdout.write(self.style.WARNING("[setup_admin] IMPORTANT: Remove CAMPUS_ADMIN_PASSWORD from environment variables now!"))
