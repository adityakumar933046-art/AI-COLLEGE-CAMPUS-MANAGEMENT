from django import forms
from .models import AcademicEvent

class AcademicEventForm(forms.ModelForm):
    class Meta:
        model = AcademicEvent
        fields = [
            "title",
            "description",
            "category",
            "priority",
            "target",
            "department",
            "course",
            "semester",
            "location",
            "start_time",
            "end_time",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter academic event title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Enter event details, agenda, or location guidelines..."}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "target": forms.Select(attrs={"class": "form-select"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Semester (Optional)"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Auditorium, Hall, Room Number (Optional)"}),
            "start_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
