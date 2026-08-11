import os
from django import forms
from django.utils import timezone
from .models import Leave


class LeaveForm(forms.ModelForm):

    class Meta:
        model = Leave
        fields = [
            "leave_type",
            "from_date",
            "to_date",
            "reason",
            "medical_certificate",
        ]
        widgets = {
            "leave_type": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_leave_type"
                }
            ),
            "from_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),
            "to_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),
            "reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter detailed reason for academic leave..."
                }
            ),
            "medical_certificate": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.jpg,.jpeg,.png"
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        leave_type = cleaned_data.get("leave_type")
        from_date = cleaned_data.get("from_date")
        to_date = cleaned_data.get("to_date")
        cert = cleaned_data.get("medical_certificate")

        if from_date and to_date:
            if from_date > to_date:
                raise forms.ValidationError("End date cannot be before start date.")

        if leave_type == "MEDICAL":
            if not cert:
                raise forms.ValidationError("Medical Certificate is required for Medical Leave.")
            
        if cert:
            ext = os.path.splitext(cert.name)[1].lower()
            allowed = [".pdf", ".jpg", ".jpeg", ".png"]
            if ext not in allowed:
                raise forms.ValidationError(f"Invalid file format '{ext}'. Allowed formats: PDF, JPG, JPEG, PNG.")
            if cert.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Medical Certificate file size must not exceed 5 MB.")

        return cleaned_data


class LeaveStatusForm(forms.ModelForm):

    class Meta:
        model = Leave
        fields = ["status", "remarks"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter review remarks or reason for rejection..."
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        remarks = cleaned_data.get("remarks")

        if status == "REJECTED" and not (remarks and remarks.strip()):
            raise forms.ValidationError("Review remarks are required when rejecting a leave application.")

        return cleaned_data
