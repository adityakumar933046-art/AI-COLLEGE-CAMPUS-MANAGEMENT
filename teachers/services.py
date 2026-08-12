import random
import string

import pandas as pd

from django.contrib.auth import get_user_model
from django.db import transaction

from departments.models import Department
from .models import TeacherProfile

User = get_user_model()


# ==========================================================
# PASSWORD GENERATOR
# ==========================================================

def generate_password(length=10):
    characters = (
        string.ascii_letters
        + string.digits
        + "@#$%&*"
    )

    return "".join(
        random.choice(characters)
        for _ in range(length)
    )


# ==========================================================
# USERNAME GENERATOR
# ==========================================================

def generate_username(first_name, employee_id):

    username = f"{first_name.lower()}{employee_id}"

    original = username
    count = 1

    while User.objects.filter(username=username).exists():
        username = f"{original}{count}"
        count += 1

    return username


# ==========================================================
# CREATE SINGLE TEACHER
# ==========================================================

@transaction.atomic
@transaction.atomic
def create_teacher(data, created_by=None):
    dob_val = data.get("date_of_birth") or None
    if dob_val == "": dob_val = None
    
    jd_val = data.get("joining_date") or None
    if jd_val == "": jd_val = None

    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    email = data.get("email", "").strip().lower()
    employee_id = str(data.get("employee_id")).strip()

    username = generate_username(
        first_name,
        employee_id,
    )

    # Use entered password if available,
    # otherwise generate one automatically.
    password = (
        data.get("password")
        or generate_password()
    )

    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        role="TEACHER",
    )
    user.must_change_password = True
    user.save()

    teacher, _ = TeacherProfile.objects.get_or_create(
        user=user,
        defaults={"employee_id": employee_id}
    )
    teacher.employee_id = employee_id
    teacher.designation = data.get("designation") or "Assistant Professor"
    teacher.department = data.get("department")
    teacher.qualification = data.get("qualification") or ""
    teacher.specialization = data.get("specialization") or ""
    teacher.experience = data.get("experience", 0)
    teacher.employment_type = data.get("employment_type", "FULL_TIME")
    teacher.phone = data.get("phone") or ""
    teacher.gender = data.get("gender", "")
    teacher.date_of_birth = dob_val
    teacher.blood_group = data.get("blood_group", "")
    teacher.joining_date = jd_val
    teacher.office_room = data.get("office_room", "")
    teacher.is_hod = data.get("is_hod", False)
    teacher.status = data.get("status", "ACTIVE")
    if data.get("photo"):
        teacher.photo = data.get("photo")
    teacher.created_by = created_by
    teacher.updated_by = created_by
    teacher.save()

    return {
        "teacher": teacher,
        "user": user,
        "username": username,
        "password": password,
    }
# ==========================================================
# BULK IMPORT TEACHERS
# ==========================================================

def bulk_import_teachers(
    excel_file,
    created_by=None,
):

    dataframe = pd.read_excel(excel_file)

    success = []
    credentials = []
    errors = []

    for index, row in dataframe.iterrows():

        try:

            employee_id = str(
                row["employee_id"]
            ).strip()

            email = str(
                row["email"]
            ).strip().lower()

            if TeacherProfile.objects.filter(
                employee_id=employee_id
            ).exists():

                errors.append({
                    "row": index + 2,
                    "employee_id": employee_id,
                    "error": "Employee ID already exists",
                })

                continue

            if User.objects.filter(
                email=email
            ).exists():

                errors.append({
                    "row": index + 2,
                    "employee_id": employee_id,
                    "error": "Email already exists",
                })

                continue

            result = create_teacher(

                data={

                    "first_name": str(
                        row["first_name"]
                    ).strip(),

                    "last_name": str(
                        row.get("last_name", "")
                    ).strip(),

                    "email": email,

                    "employee_id": employee_id,

                    "designation": row.get(
                        "designation"
                    ),

                    "department": Department.objects.filter(
                        id=row.get("department")
                    ).first(),

                    "qualification": row.get(
                        "qualification",
                        "",
                    ),

                    "specialization": row.get(
                        "specialization",
                        "",
                    ),

                    "experience": row.get(
                        "experience",
                        0,
                    ),

                    "employment_type": row.get(
                        "employment_type",
                        "FULL_TIME",
                    ),

                    "phone": str(
                        row.get("phone", "")
                    ),

                    "gender": row.get(
                        "gender",
                        "",
                    ),

                    "date_of_birth": row.get(
                        "date_of_birth",
                        None,
                    ),

                    "blood_group": row.get(
                        "blood_group",
                        "",
                    ),

                    "joining_date": row.get(
                        "joining_date",
                        None,
                    ),

                    "office_room": row.get(
                        "office_room",
                        "",
                    ),

                    "is_hod": row.get(
                        "is_hod",
                        False,
                    ),

                    "status": row.get(
                        "status",
                        "ACTIVE",
                    ),
                },

                created_by=created_by,
            )

            success.append(
                result["teacher"]
            )

            credentials.append({

                "Employee ID": employee_id,

                "Name": (
                    result["teacher"].user.first_name
                    + " "
                    + result["teacher"].user.last_name
                ).strip(),

                "Username": result["username"],

                "Password": result["password"],

            })

        except Exception as e:

            errors.append({

                "row": index + 2,

                "employee_id": row.get(
                    "employee_id",
                    "",
                ),

                "error": str(e),

            })

    return {

        "success_count": len(success),

        "error_count": len(errors),

        "success": success,

        "credentials": credentials,

        "errors": errors,

    }

# ==========================================================
# EXPORT CREDENTIALS
# ==========================================================

def export_credentials(credentials):
    return pd.DataFrame(credentials)


# ==========================================================
# EXPORT ERROR REPORT
# ==========================================================

def export_error_report(errors):
    return pd.DataFrame(errors)


# ==========================================================
# EXPORT TEACHERS EXCEL
# ==========================================================

def export_teachers_excel(queryset):

    data = []

    for teacher in queryset.select_related(
        "user",
        "department",
    ):

        data.append({

            "Employee ID": teacher.employee_id,

            "Full Name": (
                f"{teacher.user.first_name} "
                f"{teacher.user.last_name}"
            ).strip(),

            "Username": teacher.user.username,

            "Email": teacher.user.email,

            "Department": (
                teacher.department.name
                if teacher.department
                else ""
            ),

            "Designation": teacher.designation,

            "Qualification": teacher.qualification,

            "Specialization": teacher.specialization,

            "Experience": teacher.experience,

            "Employment Type": teacher.employment_type,

            "Phone": teacher.phone,

            "Gender": teacher.gender,

            "Blood Group": teacher.blood_group,

            "Joining Date": teacher.joining_date,

            "Office Room": teacher.office_room,

            "HOD": teacher.is_hod,

            "Status": teacher.status,

        })

    return pd.DataFrame(data)


# ==========================================================
# EXPORT TEACHERS CSV
# ==========================================================

def export_teachers_csv(queryset):
    return export_teachers_excel(queryset)