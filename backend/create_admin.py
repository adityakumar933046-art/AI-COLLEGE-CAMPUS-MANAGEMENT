"""
One-time script to create the initial admin superuser.
Run via:  python create_admin.py
Delete this file after use.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounts.models import User

USERNAME = "admin"
EMAIL = "adityakumar933046@gmail.com"
PASSWORD = "Admin@campus2026"

if User.objects.filter(username=USERNAME).exists():
    print(f"User '{USERNAME}' already exists. Skipping.")
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
    print(f"Admin user '{USERNAME}' created successfully.")
