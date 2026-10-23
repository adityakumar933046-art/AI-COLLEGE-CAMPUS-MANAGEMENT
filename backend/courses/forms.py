from django import forms
from django.core.exceptions import ValidationError

from .models import Course, CourseMaterial


# ==========================================
# COURSE CREATE / UPDATE FORM
# ==========================================

class CourseCreateForm(forms.ModelForm):

    class Meta:

        model = Course

        fields = [
            "code",
            "name",
            "description",
            "department",
            "teacher",
            "semester",
            "credits",
            "status",
        ]

        widgets = {

            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Course Code",
            }),

            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Course Name",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
            }),

            "department": forms.Select(attrs={
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

            "credits": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 10,
            }),

            "status": forms.Select(attrs={
                "class": "form-select",
            }),

        }

    def clean_code(self):

        code = self.cleaned_data.get("code")

        if Course.objects.filter(code__iexact=code).exists():

            raise ValidationError(
                "Course code already exists."
            )

        return code

    def clean_semester(self):

        semester = self.cleaned_data.get("semester")

        if semester < 1 or semester > 8:

            raise ValidationError(
                "Semester must be between 1 and 8."
            )

        return semester

    def clean_credits(self):

        credits = self.cleaned_data.get("credits")

        if credits < 1 or credits > 10:

            raise ValidationError(
                "Credits must be between 1 and 10."
            )

        return credits


# ==========================================
# UPDATE FORM
# ==========================================

class CourseUpdateForm(CourseCreateForm):

    def clean_code(self):

        code = self.cleaned_data.get("code")

        if Course.objects.exclude(
            pk=self.instance.pk
        ).filter(
            code__iexact=code
        ).exists():

            raise ValidationError(
                "Course code already exists."
            )

        return code


# ==========================================
# COURSE MATERIAL FORM
# ==========================================

class CourseMaterialForm(forms.ModelForm):

    class Meta:

        model = CourseMaterial

        fields = [
            "course",
            "title",
            "file",
        ]

        widgets = {

            "course": forms.Select(attrs={
                "class": "form-select",
            }),

            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Material Title",
            }),

            "file": forms.FileInput(attrs={
                "class": "form-control",
            }),

        }

    def clean_file(self):

        file = self.cleaned_data.get("file")

        if not file:

            raise ValidationError(
                "Please select a file."
            )

        if file.size > 20 * 1024 * 1024:

            raise ValidationError(
                "Maximum file size is 20 MB."
            )

        return file


# ==========================================
# EXCEL IMPORT FORM
# ==========================================

class CourseImportForm(forms.Form):

    excel_file = forms.FileField(

        label="Upload Excel File",

        widget=forms.FileInput(
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
                "Only Excel (.xlsx/.xls) files are allowed."
            )

        if file.size > 10 * 1024 * 1024:

            raise ValidationError(
                "Maximum file size is 10 MB."
            )

        return file