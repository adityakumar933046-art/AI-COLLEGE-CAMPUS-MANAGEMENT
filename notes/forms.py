from django import forms
from courses.models import Course
from .models import Note

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = [
            "title",
            "description",
            "course",
            "unit_topic",
            "material_type",
            "file",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Database Normalization & 3NF"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Summary of topics covered, key formulas, or reference links..."}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "unit_topic": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Unit 3 / Relational Algebra"}),
            "material_type": forms.Select(attrs={"class": "form-select"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and user.role == "TEACHER" and hasattr(user, "teacher_profile"):
            self.fields["course"].queryset = Course.objects.filter(teacher=user.teacher_profile)

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            allowed_extensions = [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".csv", ".txt"]
            filename = file.name.lower()
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError("Only PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, CSV, and TXT files are allowed.")
            if file.size > 20 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 20 MB.")
        return file
