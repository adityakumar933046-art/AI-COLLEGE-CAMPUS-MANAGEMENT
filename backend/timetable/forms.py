from departments.models import Department
from courses.models import Course
from teachers.models import TeacherProfile
from django import forms
from django.core.exceptions import ValidationError

from .models import Timetable


# ==========================================================
# CREATE / UPDATE FORM
# ==========================================================

class TimetableForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = Department.objects.all().order_by("name")
        self.fields["department"].empty_label = "-- Select Department --"
        self.fields["course"].queryset = Course.objects.all().order_by("name")
        self.fields["course"].empty_label = "-- Select Course --"
        self.fields["teacher"].queryset = TeacherProfile.objects.select_related("user").all()
        self.fields["teacher"].empty_label = "-- Select Faculty --"
        self.fields["is_active"].initial = True


    class Meta:

        model = Timetable

        fields = [
            "department",
            "semester",
            "section",
            "course",
            "teacher",
            "day",
            "start_time",
            "end_time",
            "classroom",
            "is_active",
        ]

        widgets = {

            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "semester": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 8,
                }
            ),

            "section": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "course": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "teacher": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "day": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "start_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),

            "end_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                }
            ),

            "classroom": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Classroom",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        department = cleaned_data.get("department")
        semester = cleaned_data.get("semester")
        section = cleaned_data.get("section")
        teacher = cleaned_data.get("teacher")
        day = cleaned_data.get("day")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        classroom = cleaned_data.get("classroom")

        if start_time and end_time:

            if start_time >= end_time:

                raise ValidationError(
                    "End time must be greater than start time."
                )

        if teacher and day and start_time:

            qs = Timetable.objects.filter(
                teacher=teacher,
                day=day,
                start_time=start_time,
            )

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():

                raise ValidationError(
                    "Teacher already has another class at this time."
                )

        if classroom and day and start_time:

            qs = Timetable.objects.filter(
                classroom=classroom,
                day=day,
                start_time=start_time,
            )

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():

                raise ValidationError(
                    "Classroom already occupied."
                )

        if (
            department
            and semester
            and section
            and day
            and start_time
        ):

            qs = Timetable.objects.filter(
                department=department,
                semester=semester,
                section=section,
                day=day,
                start_time=start_time,
            )

            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():

                raise ValidationError(
                    "Duplicate timetable found."
                )

        return cleaned_data


# ==========================================================
# IMPORT FORM
# ==========================================================

class TimetableImportForm(forms.Form):

    timetable_file = forms.FileField(

        label="Upload Excel / CSV",

        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": ".xlsx,.xls,.csv",
            }
        )
    )

    def clean_timetable_file(self):

        file = self.cleaned_data["timetable_file"]

        if not file.name.endswith(
            (
                ".xlsx",
                ".xls",
                ".csv",
            )
        ):

            raise ValidationError(
                "Only Excel or CSV files are allowed."
            )

        if file.size > 10 * 1024 * 1024:

            raise ValidationError(
                "Maximum file size is 10 MB."
            )

        return file


# ==========================================================
# FILTER FORM
# ==========================================================

class TimetableFilterForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by("name"),
        required=False,
        empty_label="All Departments",
        widget=forms.Select(attrs={"class": "form-select"}),
    )


    search = forms.CharField(

        required=False,

        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search...",
            }
        ),
    )

    semester = forms.IntegerField(

        required=False,

        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Semester",
            }
        ),
    )

    section = forms.ChoiceField(

        required=False,

        choices=[
            ("", "All Sections"),
        ] + list(Timetable.SECTION_CHOICES),

        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    day = forms.ChoiceField(

        required=False,

        choices=[
            ("", "All Days"),
        ] + list(Timetable.DAY_CHOICES),

        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )