import os
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Automatically create or update a superuser using environment variables or safe defaults."

    def handle(self, *args, **options):
        username = (
            os.environ.get("SUPERUSER_USERNAME", "").strip()
            or os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
            or os.environ.get("CAMPUS_ADMIN_USERNAME", "").strip()
            or "admin"
        )
        email = (
            os.environ.get("SUPERUSER_EMAIL", "").strip()
            or os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
            or os.environ.get("CAMPUS_ADMIN_EMAIL", "").strip()
            or "smartcampus.in.org@gmail.com"
        )
        password = (
            os.environ.get("SUPERUSER_PASSWORD", "").strip()
            or os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()
            or os.environ.get("CAMPUS_ADMIN_PASSWORD", "").strip()
            or "admin"
        )

        user = User.objects.filter(username=username).first() or User.objects.filter(email=email).first()
        if not user:
            user = User(username=username, email=email)

        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.is_active_account = True
        user.must_change_password = False
        user.role = User.Roles.ADMIN
        user.save()

        self.stdout.write(self.style.SUCCESS(f"Superuser '{user.username}' ({user.email}) ready with password '{password}'."))
