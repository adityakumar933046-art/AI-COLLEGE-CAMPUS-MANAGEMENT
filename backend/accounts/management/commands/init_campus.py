import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from accounts.models import User


class Command(BaseCommand):
    help = "Auto-initialize campus database: apply migrations, seed initial data, and configure verified login credentials."

    def handle(self, *args, **options):
        self.stdout.write("[init_campus] Checking database state...")

        # 1. Run migrations
        call_command("migrate", "--noinput")

        # 2. Check if student data exists; if not, load seed_data.json fixture
        student_count = User.objects.filter(role="STUDENT").count()
        if student_count == 0:
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
                self.stdout.write(f"[init_campus] Student accounts not found. Loading fixture from {fixture_path}...")
                try:
                    call_command("loaddata", fixture_path)
                    self.stdout.write(self.style.SUCCESS("[init_campus] Initial campus data loaded successfully!"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"[init_campus] Warning loading seed_data: {e}"))
            else:
                self.stdout.write("[init_campus] No seed_data.json found. Skipping fixture loading.")
        else:
            self.stdout.write(f"[init_campus] Database already has {student_count} student(s) and {User.objects.count()} total user(s).")

        # 3. Superuser creation from Environment variables or fallback
        env_super_user = (
            os.environ.get("SUPERUSER_USERNAME", "").strip()
            or os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
            or os.environ.get("CAMPUS_ADMIN_USERNAME", "").strip()
            or "admin"
        )
        env_super_email = (
            os.environ.get("SUPERUSER_EMAIL", "").strip()
            or os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
            or os.environ.get("CAMPUS_ADMIN_EMAIL", "").strip()
            or "admin@smartcampus.local"
        )
        env_super_pass = (
            os.environ.get("SUPERUSER_PASSWORD", "").strip()
            or os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()
            or os.environ.get("CAMPUS_ADMIN_PASSWORD", "").strip()
            or "admin"
        )

        admin_user, _ = User.objects.get_or_create(
            username=env_super_user,
            defaults={
                "email": env_super_email,
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
                "is_active_account": True,
                "must_change_password": False,
            }
        )
        admin_user.set_password(env_super_pass)
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.is_active_account = True
        admin_user.must_change_password = False
        admin_user.role = "ADMIN"
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f"[init_campus] Superuser '{env_super_user}' ({admin_user.email}) verified."))

        # 4. Guarantee specific requested accounts exist and have password 'admin'
        accounts_to_ensure = [
            ("ADITYA3D", "adityakumar933046@gmail.com", "ADMIN", True, True, "admin"),
            ("aditya25006", "adityakumar933050@gmail.com", "STUDENT", False, False, "admin"),
            ("virus5556222", "adityakumar933047@gmail.com", "TEACHER", False, False, "admin"),
        ]

        for uname, uemail, urole, is_staff, is_super, upass in accounts_to_ensure:
            user_obj = User.objects.filter(username=uname).first() or User.objects.filter(email=uemail).first()
            if not user_obj:
                user_obj = User(username=uname, email=uemail)

            user_obj.username = uname
            user_obj.email = uemail
            user_obj.role = urole
            user_obj.is_staff = is_staff
            user_obj.is_superuser = is_super
            user_obj.is_active = True
            user_obj.is_active_account = True
            user_obj.must_change_password = False
            user_obj.set_password(upass)
            user_obj.save()

            # Ensure profile exists for student and teacher
            if urole == "STUDENT":
                try:
                    from students.models import StudentProfile
                    StudentProfile.objects.get_or_create(user=user_obj, defaults={"roll_no": uname})
                except Exception as ex:
                    self.stdout.write(f"[init_campus] StudentProfile notice: {ex}")
            elif urole == "TEACHER":
                try:
                    from teachers.models import TeacherProfile
                    TeacherProfile.objects.get_or_create(user=user_obj, defaults={"employee_id": uname})
                except Exception as ex:
                    self.stdout.write(f"[init_campus] TeacherProfile notice: {ex}")

            self.stdout.write(self.style.SUCCESS(f"[init_campus] Account '{uname}' ({uemail}) [{urole}] verified with password '{upass}'."))

        self.stdout.write(self.style.SUCCESS("[init_campus] Database initialization complete."))
