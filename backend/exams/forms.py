from django import forms
from django.db.models import Q
from .models import Exam, ExamSchedule


class ExamForm(forms.ModelForm):

    class Meta:
        model = Exam
        fields = [
            "name",
            "exam_type",
            "department",
            "semester",
            "start_date",
            "end_date",
            "status",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Mid-Term Semester Examinations 2026"}),
            "exam_type": forms.Select(attrs={"class": "form-select"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 8}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date cannot be before start date.")

        return cleaned_data


class ExamScheduleForm(forms.ModelForm):

    class Meta:
        model = ExamSchedule
        fields = [
            "course",
            "date",
            "start_time",
            "end_time",
            "room",
            "section",
            "invigilator",
            "instructions",
        ]
        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "room": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Room A-204"}),
            "section": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. A"}),
            "invigilator": forms.Select(attrs={"class": "form-select"}),
            "instructions": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Exam instructions..."}),
        }

    def __init__(self, *args, **kwargs):
        self.exam = kwargs.pop("exam", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        room = cleaned_data.get("room")
        section = cleaned_data.get("section")
        invigilator = cleaned_data.get("invigilator")

        if start_time and end_time:
            if start_time >= end_time:
                raise forms.ValidationError("End time must be after start time.")

        if self.exam and date:
            if not (self.exam.start_date <= date <= self.exam.end_date):
                raise forms.ValidationError(f"Schedule date must be within the exam date range ({self.exam.start_date} to {self.exam.end_date}).")

        # Conflict checks
        if date and start_time and end_time:
            time_overlap = Q(start_time__lt=end_time, end_time__gt=start_time)
            instance_pk = self.instance.pk if self.instance else None

            # 1. Room Conflict
            if room:
                room_qs = ExamSchedule.objects.filter(date=date, room__iexact=room).filter(time_overlap)
                if instance_pk:
                    room_qs = room_qs.exclude(pk=instance_pk)
                if room_qs.exists():
                    conf = room_qs.first()
                    raise forms.ValidationError(f"Room '{room}' is already booked for course '{conf.course.code}' during {conf.start_time} - {conf.end_time}.")

            # 2. Invigilator Conflict
            if invigilator:
                inv_qs = ExamSchedule.objects.filter(date=date, invigilator=invigilator).filter(time_overlap)
                if instance_pk:
                    inv_qs = inv_qs.exclude(pk=instance_pk)
                if inv_qs.exists():
                    conf = inv_qs.first()
                    raise forms.ValidationError(f"Invigilator {invigilator.full_name} is already assigned to an exam in room {conf.room} during {conf.start_time} - {conf.end_time}.")

            # 3. Student Section Conflict
            if self.exam and section:
                sec_qs = ExamSchedule.objects.filter(
                    date=date,
                    section__iexact=section,
                    exam__department=self.exam.department,
                    exam__semester=self.exam.semester
                ).filter(time_overlap)
                if instance_pk:
                    sec_qs = sec_qs.exclude(pk=instance_pk)
                if sec_qs.exists():
                    conf = sec_qs.first()
                    raise forms.ValidationError(f"Section '{section}' already has exam '{conf.course.code}' scheduled during {conf.start_time} - {conf.end_time}.")

        return cleaned_data
