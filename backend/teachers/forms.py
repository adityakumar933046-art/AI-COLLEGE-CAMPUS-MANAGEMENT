from django import forms
from django.core.exceptions import ValidationError

from .models import TeacherProfile


# ==========================================================
# TEACHER CREATE FORM
# ==========================================================

class TeacherCreateForm(forms.ModelForm):

    
    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise ValidationError("Email address is required.")
        from accounts.models import User
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user or faculty account with this email address already exists.")
        return email

    def clean_employee_id(self):
        employee_id = str(self.cleaned_data.get("employee_id", "")).strip()
        if not employee_id:
            raise ValidationError("Employee ID is required.")
        if TeacherProfile.objects.filter(employee_id=employee_id).exists():
            raise ValidationError("A teacher with this Employee ID already exists.")
        return employee_id


    class Meta:

        model = TeacherProfile

        fields = [
            "employee_id",
            "department",
            "designation",
            "qualification",
            "specialization",
            "experience",
            "employment_type",
            "phone",
            "photo",
            "gender",
            "date_of_birth",
            "blood_group",
            "joining_date",
            "office_room",
            "is_hod",
            "status",
        ]

        widgets = {

            "employee_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Employee ID",
                }
            ),

            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "designation": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Designation",
                }
            ),

            "qualification": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Qualification",
                }
            ),

            "specialization": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Specialization",
                }
            ),

            "experience": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                }
            ),

            "employment_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Phone Number",
                }
            ),

            "photo": forms.FileInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "blood_group": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Blood Group",
                }
            ),

            "joining_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "office_room": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Office Room",
                }
            ),

            "is_hod": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    # ==========================================================
    # VALIDATIONS
    # ==========================================================

    def clean_employee_id(self):

        employee_id = self.cleaned_data.get("employee_id")

        if employee_id and TeacherProfile.objects.filter(
            employee_id__iexact=employee_id
        ).exists():

            raise ValidationError(
                "Employee ID already exists."
            )

        return employee_id

    def clean_phone(self):

        phone = self.cleaned_data.get("phone")

        if phone:

            if not phone.isdigit():

                raise ValidationError(
                    "Phone number must contain only digits."
                )

            if len(phone) != 10:

                raise ValidationError(
                    "Phone number must contain exactly 10 digits."
                )

        return phone
    
    # ==========================================================
# TEACHER UPDATE FORM
# ==========================================================

class TeacherUpdateForm(TeacherCreateForm):

    def clean_employee_id(self):

        employee_id = self.cleaned_data.get("employee_id")

        if employee_id and TeacherProfile.objects.exclude(
            pk=self.instance.pk
        ).filter(
            employee_id__iexact=employee_id
        ).exists():

            raise ValidationError(
                "Employee ID already exists."
            )

        return employee_id

    def clean_phone(self):

        phone = self.cleaned_data.get("phone")

        if phone:

            if not phone.isdigit():

                raise ValidationError(
                    "Phone number must contain only digits."
                )

            if len(phone) != 10:

                raise ValidationError(
                    "Phone number must contain exactly 10 digits."
                )

        return phone
    
    # ==========================================================
# TEACHER EXCEL IMPORT FORM
# ==========================================================

class TeacherExcelImportForm(forms.Form):

    excel_file = forms.FileField(

        label="Upload Excel File",

        help_text="Upload .xlsx or .xls file",

        widget=forms.FileInput(

            attrs={
                "class": "form-control",
                "accept": ".xlsx,.xls",
            }

        ),
    )

    def clean_excel_file(self):

        file = self.cleaned_data.get("excel_file")

        if not file:

            raise ValidationError(
                "Please select an Excel file."
            )

        if not file.name.lower().endswith(
            (".xlsx", ".xls")
        ):

            raise ValidationError(
                "Only Excel (.xlsx or .xls) files are allowed."
            )

        if file.size > 5 * 1024 * 1024:

            raise ValidationError(
                "Maximum file size is 5 MB."
            )

        return file
    
    # ==========================================================
# TEACHER PROFILE FORM
# ==========================================================

class TeacherProfileForm(TeacherCreateForm):

    class Meta(TeacherCreateForm.Meta):

        exclude = [
            "user",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]