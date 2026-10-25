import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from accounts.models import User


class Command(BaseCommand):
    help = "Auto-initialize campus database: apply migrations, seed initial data if empty, and configure admin."

    def handle(self, *args, **options):
        self.stdout.write("[init_campus] Checking database state...")

        # 1. Run migrations
        call_command("migrate", "--noinput")

        # 2. Check if database has users; if empty, load seed_data.json
        if not User.objects.exists():
            # Check possible locations for seed_data.json
            candidate_paths = [
                os.path.join(settings.BASE_DIR, "seed_data.json"),
                os.path.join(settings.BASE_DIR, "..", "seed_data.json"),
                "seed_data.json",
                "backend/seed_data.json",
            ]
            fixture_path = None
            for p in candidate_paths:
                if os.path.exists(p):
                    fixture_path = os.path.abspath(p)
                    break

            if fixture_path:
                self.stdout.write(f"[init_campus] Database is empty. Loading initial fixture from {fixture_path}...")
                try:
                    call_command("loaddata", fixture_path)
                    self.stdout.write(self.style.SUCCESS("[init_campus] Initial campus data loaded successfully!"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"[init_campus] Warning loading seed_data: {e}"))
            else:
                self.stdout.write("[init_campus] No seed_data.json found. Skipping fixture loading.")
        else:
            self.stdout.write(f"[init_campus] Database already initialized with {User.objects.count()} user(s).")

        # 3. Ensure admin user exists (from environment or default fallback)
        admin_username = os.environ.get("CAMPUS_ADMIN_USERNAME", "").strip() or "admin"
        admin_email = os.environ.get("CAMPUS_ADMIN_EMAIL", "").strip() or "admin@smartcampus.local"
        admin_password = os.environ.get("CAMPUS_ADMIN_PASSWORD", "").strip() or "admin"

        admin_user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "email": admin_email,
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
                "is_active_account": True,
                "must_change_password": False,
            }
        )
        if created:
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"[init_campus] Created admin user '{admin_username}'."))
        else:
            needs_save = False
            if admin_user.role != "ADMIN":
                admin_user.role = "ADMIN"
                needs_save = True
            if not admin_user.is_superuser or not admin_user.is_staff:
                admin_user.is_superuser = True
                admin_user.is_staff = True
                needs_save = True
            if not admin_user.is_active:
                admin_user.is_active = True
                needs_save = True
            if needs_save:
                admin_user.save()
            self.stdout.write(f"[init_campus] Admin user '{admin_username}' is verified.")

        self.stdout.write(self.style.SUCCESS("[init_campus] Database initialization complete."))
