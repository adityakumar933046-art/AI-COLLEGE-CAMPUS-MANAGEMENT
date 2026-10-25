"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR if BASE_DIR.name == "backend" else BASE_DIR / "backend"
ROOT_DIR = BASE_DIR.parent if BASE_DIR.name == "backend" else BASE_DIR

for p in [str(ROOT_DIR), str(BACKEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Safe auto-initialization hook on startup (collects static files, runs migrations, seeds admin/users if empty)
try:
    from django.core.management import call_command
    print("[WSGI] Running automatic startup static files collection (collectstatic)...")
    call_command("collectstatic", "--noinput")
    print("[WSGI] Static files collected successfully.")
    print("[WSGI] Running automatic startup database check (init_campus)...")
    call_command("init_campus")
    print("[WSGI] Startup database check completed successfully.")
except Exception as e:
    print(f"[WSGI] Auto-init notice / warning: {e}")
