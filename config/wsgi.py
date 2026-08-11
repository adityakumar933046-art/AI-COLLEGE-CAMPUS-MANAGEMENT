"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Automatic production database self-healing check
try:
    from django.core.management import call_command
    from django.db import connection
    tables = connection.introspection.table_names()
    if 'accounts_user' not in tables:
        print("[WSGI] Database tables missing. Running automatic migrations...")
        call_command('migrate', interactive=False)

        # Create default Admin user if missing
        from accounts.models import User
        if not User.objects.filter(username="ADITYA3D").exists():
            print("[WSGI] Creating default Admin user ADITYA3D...")
            admin = User.objects.create(
                username="ADITYA3D",
                email="adityakumar933046@gmail.com",
                role="ADMIN",
                is_staff=True,
                is_superuser=True
            )
            admin.set_password("Aditya@123")
            admin.must_change_password = False
            admin.save()
            print("[WSGI] Admin account created successfully.")
except Exception as e:
    print(f"[WSGI] Database auto-migration notice: {e}")
