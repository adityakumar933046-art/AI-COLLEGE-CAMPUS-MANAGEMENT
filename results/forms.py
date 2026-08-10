from django import forms
from .models import Result


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = [
            "student",
            "course",
            "teacher",
            "exam_type",
            "semester",
            "marks_obtained",
            "total_marks",
            "is_published",
            "remarks",
        ]
        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "teacher": forms.Select(attrs={"class": "form-select"}),
            "exam_type": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 8}),
            "marks_obtained": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "total_marks": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "remarks": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional remarks"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        marks_obtained = cleaned_data.get("marks_obtained")
        total_marks = cleaned_data.get("total_marks")
        semester = cleaned_data.get("semester")

        if semester and (semester < 1 or semester > 8):
            raise forms.ValidationError("Semester must be between 1 and 8.")

        if marks_obtained is not None and total_marks is not None:
            if marks_obtained > total_marks:
                raise forms.ValidationError("Marks obtained cannot be greater than total marks.")

        return cleaned_data
