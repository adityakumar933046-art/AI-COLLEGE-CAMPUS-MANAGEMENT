from django import forms
from django.core.exceptions import ValidationError

from .models import AttendanceSession, Attendance


# ==========================================
# ATTENDANCE SESSION FORM
# ==========================================

class AttendanceSessionForm(forms.ModelForm):

    class Meta:

        model = AttendanceSession

        fields = [
            "department",
            "course",
            "teacher",
            "semester",
            "section",
            "lecture_no",
            "attendance_date",
            "remarks",
            "status",
        ]

        widgets = {

            "department": forms.Select(attrs={
                "class": "form-select",
            }),

            "course": forms.Select(attrs={
                "class": "form-select",
            }),

            "teacher": forms.Select(attrs={
                "class": "form-select",
            }),

            "semester": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 8,
            }),

            "section": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Section (A/B/C)",
            }),

            "lecture_no": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 10,
            }),

            "attendance_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),

            "remarks": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),

            "status": forms.Select(attrs={
                "class": "form-select",
            }),

        }

    def clean_lecture_no(self):

        lecture = self.cleaned_data["lecture_no"]

        if lecture < 1 or lecture > 10:

            raise ValidationError(
                "Lecture number must be between 1 and 10."
            )

        return lecture


# ==========================================
# STUDENT ATTENDANCE FORM
# ==========================================

class AttendanceForm(forms.ModelForm):

    class Meta:

        model = Attendance

        fields = [
            "student",
            "status",
            "remarks",
        ]

        widgets = {

            "student": forms.Select(attrs={
                "class": "form-select",
            }),

            "status": forms.Select(attrs={
                "class": "form-select",
            }),

            "remarks": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Remarks (Optional)",
            }),

        }


# ==========================================
# FILTER FORM
# ==========================================

class AttendanceFilterForm(forms.Form):

    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Department",
        })
    )

    semester = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
        })
    )

    section = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
        })
    )

    course = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
        })
    )

    teacher = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
        })
    )

    attendance_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date",
        })
    )

    status = forms.ChoiceField(

        required=False,

        choices=[
            ("", "All"),
            ("PRESENT", "Present"),
            ("ABSENT", "Absent"),
            ("LATE", "Late"),
            ("MEDICAL", "Medical Leave"),
        ],

        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )