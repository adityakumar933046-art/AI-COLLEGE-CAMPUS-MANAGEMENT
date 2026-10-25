"""
Django management command to create an admin user interactively.
Password is entered at the prompt — never stored in source code.

Usage:
    python manage.py create_campus_admin --username collegeadmin --email admin@example.com
"""
import getpass

from django.core.management.base import BaseCommand, CommandError
from accounts.models import User


class Command(BaseCommand):
    help = "Create a campus admin user with the ADMIN role (interactive password prompt)."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True, help="Username for the admin account.")
        parser.add_argument("--email", required=True, help="Email for the admin account.")

    def handle(self, *args, **options):
        username = options["username"].strip()
        email = options["email"].strip().lower()

        # Check for existing user
        if User.objects.filter(username=username).exists():
            existing = User.objects.get(username=username)
            self.stdout.write(
                f"User '{username}' already exists (role={existing.role}, "
                f"is_active={existing.is_active})."
            )
            raise CommandError(
                f"User '{username}' already exists. Use Django admin or shell to modify it."
            )

        if User.objects.filter(email__iexact=email).exists():
            raise CommandError(f"A user with email '{email}' already exists.")

        # Interactive password prompt
        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")

        if not password:
            raise CommandError("Password cannot be empty.")
        if password != password_confirm:
            raise CommandError("Passwords do not match.")

        # Create the user
        user = User(
            username=username,
            email=email,
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_active_account=True,
            must_change_password=False,
        )
        user.set_password(password)  # Hashes the password
        user.save()

        self.stdout.write(self.style.SUCCESS(
            f"Admin user '{username}' created successfully with role=ADMIN."
        ))
