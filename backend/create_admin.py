"""
One-time script to create the initial admin superuser.
Delete this file after the admin account has been created.
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
    if User.objects.filter(username=USERNAME).exists():
        user = User.objects.get(username=USERNAME)
        # Ensure role is ADMIN even if user already exists
        if user.role != "ADMIN":
            user.role = "ADMIN"
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.is_active_account = True
            user.save()
            print(f"[CREATE_ADMIN] Updated existing user '{USERNAME}' role to ADMIN.")
        else:
            print(f"[CREATE_ADMIN] User '{USERNAME}' already exists with role ADMIN. Skipping.")
    else:
        user = User.objects.create_superuser(
            username=USERNAME,
            email=EMAIL,
            password=PASSWORD,
        )
        user.role = "ADMIN"
        user.is_active = True
        user.is_active_account = True
        user.must_change_password = False
        user.save()
        print(f"[CREATE_ADMIN] Admin user '{USERNAME}' created successfully with role ADMIN.")
except Exception as e:
    print(f"[CREATE_ADMIN] Error: {e}", file=sys.stderr)
    # Don't crash the deploy - just log the error
