from django import forms
from django.utils import timezone

from .models import Leave


class LeaveForm(forms.ModelForm):

    class Meta:

        model = Leave

        fields = [

            "from_date",
            "to_date",
            "reason",
            "medical_certificate",

        ]

        widgets = {

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
                    "rows": 5,
                    "placeholder": "Enter leave reason"
                }
            ),


        }

    def clean(self):

        cleaned_data = super().clean()

        from_date = cleaned_data.get("from_date")
        to_date = cleaned_data.get("to_date")

        if from_date and to_date:

            if from_date > to_date:

                raise forms.ValidationError(
                    "From date cannot be after To date."
                )

            if from_date < timezone.now().date():

                raise forms.ValidationError(
                    "From date cannot be in the past."
                )

        return cleaned_data


class LeaveStatusForm(forms.ModelForm):

    class Meta:

        model = Leave

        fields = [

            "status",
            "remarks",

        ]

        widgets = {

            "status": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Approval/Rejection remarks"
                }
            ),

        }