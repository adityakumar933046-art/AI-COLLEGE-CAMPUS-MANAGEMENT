from django.contrib import admin
from .models import Exam, ExamSchedule

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ["name", "exam_type", "department", "semester", "status", "start_date", "end_date"]
    list_filter = ["status", "exam_type", "department", "semester"]
    search_fields = ["name"]

@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ["exam", "course", "date", "start_time", "end_time", "room", "section", "invigilator"]
    list_filter = ["date", "room", "section"]
    search_fields = ["course__name", "course__code", "room"]
