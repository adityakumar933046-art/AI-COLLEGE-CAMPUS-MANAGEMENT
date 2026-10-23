from django import forms
from django.core.exceptions import ValidationError

from .models import Department


class DepartmentForm(forms.ModelForm):

    class Meta:
        model = Department

        fields = [
            "code",
            "name",
            "short_name",
            "description",
            "established_year",

            "hod",
            "hod_joining_date",

            "office_phone",
            "office_email",

            "building",

            "logo",

            "total_faculty",
            "total_students",

            "status",
        ]

        widgets = {

            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Department Code"
            }),

            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Department Name"
            }),

            "short_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Short Name"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Description"
            }),

            "established_year": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Established Year"
            }),

            "hod": forms.Select(attrs={
                "class": "form-select"
            }),

            "hod_joining_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "office_phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Office Phone"
            }),

            "office_email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Office Email"
            }),

            "building": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Building"
            }),

            "logo": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),

            "total_faculty": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "total_students": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "status": forms.Select(attrs={
                "class": "form-select"
            }),
        }

    def clean_code(self):
        code = self.cleaned_data["code"]

        qs = Department.objects.filter(code__iexact=code)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("Department code already exists.")

        return code

    def clean_name(self):
        name = self.cleaned_data["name"]

        qs = Department.objects.filter(name__iexact=name)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("Department name already exists.")

        return name

    def clean_established_year(self):
        year = self.cleaned_data.get("established_year")

        if year and (year < 1900 or year > 2100):
            raise ValidationError("Enter a valid established year.")

        return year

    def clean_total_faculty(self):
        total = self.cleaned_data.get("total_faculty")

        if total is not None and total < 0:
            raise ValidationError("Faculty count cannot be negative.")

        return total

    def clean_total_students(self):
        total = self.cleaned_data.get("total_students")

        if total is not None and total < 0:
            raise ValidationError("Student count cannot be negative.")

        return total


class DepartmentExcelImportForm(forms.Form):

    excel_file = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": ".xlsx,.xls",
            }
        )
    )

    def clean_excel_file(self):
        file = self.cleaned_data["excel_file"]

        if not file.name.endswith((".xlsx", ".xls")):
            raise ValidationError(
                "Please upload a valid Excel file."
            )

        return file