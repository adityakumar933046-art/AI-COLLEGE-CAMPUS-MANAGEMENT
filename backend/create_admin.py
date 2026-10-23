"""
One-time admin creation — runs automatically on startup.
Safe to re-run: skips if admin already exists.
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounts.models import User

USERNAME = "admin"
EMAIL = "adityakumar933046@gmail.com"
PASSWORD = "Admin@campus2026"

try:
    user, created = User.objects.get_or_create(
        username=USERNAME,
        defaults={
            "email": EMAIL,
            "role": "ADMIN",
            "is_staff": True,
            "is_superuser": True,
            "is_active": True,
            "is_active_account": True,
            "must_change_password": False,
        }
    )
    if created:
        user.set_password(PASSWORD)
        user.save()
        print(f"[CREATE_ADMIN] Admin user '{USERNAME}' created successfully.")
    else:
        # Fix role if needed
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
            print(f"[CREATE_ADMIN] Fixed user '{USERNAME}' — role set to ADMIN.")
        else:
            print(f"[CREATE_ADMIN] User '{USERNAME}' already exists with role ADMIN.")
except Exception as e:
    print(f"[CREATE_ADMIN] Error: {e}", file=sys.stderr)
