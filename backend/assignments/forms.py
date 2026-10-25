from django import forms
from django.utils import timezone
from courses.models import Course
from .models import Assignment, AssignmentSubmission


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            "title",
            "description",
            "course",
            "file",
            "due_date",
            "total_marks",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Mid-Semester Problem Set 1"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Enter detailed instructions, problem questions, or submission guidelines..."}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "total_marks": forms.NumberInput(attrs={"class": "form-control", "min": 1, "placeholder": "e.g. 100"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.role == "TEACHER" and hasattr(user, "teacher_profile"):
            self.fields["course"].queryset = Course.objects.filter(teacher=user.teacher_profile)

    def clean_due_date(self):
        due_date = self.cleaned_data["due_date"]
        if due_date < timezone.now().date():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due_date


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = [
            "file",
        ]
        widgets = {
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }


class AssignmentMarksForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = [
            "marks",
            "feedback",
        ]
        widgets = {
            "marks": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "feedback": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Enter grading feedback..."}),
        }

    def clean_marks(self):
        marks = self.cleaned_data.get("marks")
        if marks is not None:
            total = self.instance.assignment.total_marks if self.instance and self.instance.assignment else 100
            if marks < 0:
                raise forms.ValidationError("Marks cannot be negative.")
            if marks > total:
                raise forms.ValidationError(f"Marks cannot exceed total marks for this assignment ({total}).")
        return marks
