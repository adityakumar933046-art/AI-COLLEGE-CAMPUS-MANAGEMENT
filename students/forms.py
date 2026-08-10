from django import forms
from django.core.exceptions import ValidationError


from .models import StudentProfile



# ==========================================================
# STUDENT CREATE FORM
# ==========================================================

class StudentCreateForm(forms.ModelForm):


    # ==========================
    # USER INFORMATION
    # ==========================

    username = forms.CharField(
        label="Username (Optional - Auto-generated if blank)",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Auto-generated if left blank"
            }
        )
    )


    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First Name"
            }
        )
    )


    last_name = forms.CharField(
        label="Last Name",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last Name"
            }
        )
    )


    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Email Address"
            }
        )
    )


    password = forms.CharField(
        label="Password (Optional - Auto-generated if blank)",
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password"
            }
        )
    )



    
    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise ValidationError("Email address is required.")
        from accounts.models import User
        if User.objects.filter(email=email).exists():
            raise ValidationError("A student or user account with this email address already exists.")
        return email


    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'cgpa' in self.fields:
            self.fields['cgpa'].required = False
            self.fields['cgpa'].initial = 0.00
        if 'status' in self.fields:
            self.fields['status'].required = False
            self.fields['status'].initial = 'ACTIVE'


    class Meta:

        model = StudentProfile


        fields = [

            # User
            "username",
            "first_name",
            "last_name",
            "email",
            "password",


            # Academic
            "admission_no",
            "roll_no",
            "department",
            "semester",
            "section",
            "batch",
            "academic_year",
            "admission_date",


            # Personal
            "photo",
            "phone",
            "gender",
            "date_of_birth",
            "blood_group",


            # Guardian
            "father_name",
            "mother_name",
            "guardian_phone",


            # Address
            "address",
            "city",
            "state",
            "pincode",


            # Performance
            "cgpa",
            "status",

        ]



    widgets = {


        "admission_no": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "roll_no": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "department": forms.Select(
            attrs={
                "class":"form-select"
            }
        ),


        "semester": forms.NumberInput(
            attrs={
                "class":"form-control"
            }
        ),


        "section": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "batch": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "academic_year": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "admission_date": forms.DateInput(
            attrs={
                "class":"form-control",
                "type":"date"
            }
        ),


        "photo": forms.FileInput(
            attrs={
                "class":"form-control"
            }
        ),


        "phone": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "gender": forms.Select(
            attrs={
                "class":"form-select"
            }
        ),


        "date_of_birth": forms.DateInput(
            attrs={
                "class":"form-control",
                "type":"date"
            }
        ),


        "blood_group": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "father_name": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "mother_name": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "guardian_phone": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "address": forms.Textarea(
            attrs={
                "class":"form-control",
                "rows":3
            }
        ),


        "city": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "state": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "pincode": forms.TextInput(
            attrs={
                "class":"form-control"
            }
        ),


        "cgpa": forms.NumberInput(
            attrs={
                "class":"form-control",
                "step":"0.01"
            }
        ),


        "status": forms.Select(
            attrs={
                "class":"form-select"
            }
        ),

    }



    # ==========================
    # VALIDATION
    # ==========================


    def clean_roll_no(self):

        roll_no = self.cleaned_data.get(
            "roll_no"
        )


        if StudentProfile.objects.filter(
            roll_no=roll_no
        ).exists():

            raise ValidationError(
                "Roll number already exists."
            )


        return roll_no



    def clean_admission_no(self):

        admission_no = self.cleaned_data.get(
            "admission_no"
        )


        if StudentProfile.objects.filter(
            admission_no=admission_no
        ).exists():

            raise ValidationError(
                "Admission number already exists."
            )


        return admission_no



    def clean_phone(self):

        phone = self.cleaned_data.get(
            "phone"
        )


        if phone and (
            not phone.isdigit()
            or len(phone) != 10
        ):

            raise ValidationError(
                "Enter valid 10 digit phone number."
            )


        return phone





# ==========================================================
# STUDENT UPDATE FORM
# ==========================================================

class StudentUpdateForm(StudentCreateForm):


    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                "class":"form-control",
                "placeholder":"Leave blank to keep old password"
            }
        )
    )



    def clean_roll_no(self):

        roll_no = self.cleaned_data.get(
            "roll_no"
        )


        qs = StudentProfile.objects.filter(
            roll_no=roll_no
        ).exclude(
            pk=self.instance.pk
        )


        if qs.exists():

            raise ValidationError(
                "Roll number already exists."
            )


        return roll_no



    def clean_admission_no(self):

        admission_no = self.cleaned_data.get(
            "admission_no"
        )


        qs = StudentProfile.objects.filter(
            admission_no=admission_no
        ).exclude(
            pk=self.instance.pk
        )


        if qs.exists():

            raise ValidationError(
                "Admission number already exists."
            )


        return admission_no





# ==========================================================
# STUDENT PROFILE FORM
# ==========================================================

class StudentProfileForm(forms.ModelForm):


    class Meta:

        model = StudentProfile


        fields = [

            "photo",
            "phone",
            "gender",
            "date_of_birth",
            "blood_group",

            "father_name",
            "mother_name",
            "guardian_phone",

            "address",
            "city",
            "state",
            "pincode",

        ]





# ==========================================================
# EXCEL IMPORT FORM
# ==========================================================

class StudentExcelImportForm(forms.Form):


    excel_file = forms.FileField(

        label="Upload Excel File",

        widget=forms.FileInput(
            attrs={
                "class":"form-control",
                "accept":".xlsx,.xls"
            }
        )

    )



    def clean_excel_file(self):

        file = self.cleaned_data.get(
            "excel_file"
        )


        if not file:

            raise ValidationError(
                "Please select Excel file."
            )


        if not file.name.lower().endswith(
            (".xlsx",".xls")
        ):

            raise ValidationError(
                "Only Excel file allowed."
            )


        if file.size > 5*1024*1024:

            raise ValidationError(
                "Maximum file size is 5MB."
            )


        return file