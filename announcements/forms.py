from django import forms
from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            "title",
            "message",
            "category",
            "priority",
            "target",
            "department",
            "course",
            "semester",
            "status",
            "publish_at",
            "expires_at",
            "attachment",
            "is_pinned",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter academic announcement title"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "Enter detailed notice content..."}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "target": forms.Select(attrs={"class": "form-select"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Semester (Optional)"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "publish_at": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "expires_at": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "attachment": forms.FileInput(attrs={"class": "form-control"}),
            "is_pinned": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
