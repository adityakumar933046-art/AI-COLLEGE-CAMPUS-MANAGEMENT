from django import forms

from .models import QRSession


class QRSessionForm(forms.ModelForm):

    class Meta:

        model = QRSession

        fields = [

            "course",

            "teacher",

        ]

        widgets = {

            "course": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "teacher": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

        }

    def clean(self):

        cleaned_data = super().clean()

        course = cleaned_data.get("course")

        teacher = cleaned_data.get("teacher")

        if course and teacher:

            if teacher.department != course.department.name:

                raise forms.ValidationError(
                    "Selected teacher does not belong to this course department."
                )

        return cleaned_data