from django.db import models
from django.conf import settings
from departments.models import Department
from courses.models import Course
from teachers.models import TeacherProfile


class Exam(models.Model):

    EXAM_TYPE_CHOICES = (
        ("INTERNAL", "Internal Exam"),
        ("MID_TERM", "Mid-Term Examination"),
        ("PRACTICAL", "Practical Examination"),
        ("END_SEMESTER", "End-Semester Examination"),
        ("QUIZ", "Academic Quiz"),
        ("OTHER", "Other"),
    )

    STATUS_CHOICES = (
        ("DRAFT", "Draft"),
        ("PUBLISHED", "Published"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    )

    name = models.CharField(max_length=200)

    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPE_CHOICES,
        default="MID_TERM"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="exams"
    )

    semester = models.PositiveIntegerField(default=1)

    start_date = models.DateField()

    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.get_exam_type_display()}) - Sem {self.semester}"


class ExamSchedule(models.Model):

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="schedules"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="exam_schedules"
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    room = models.CharField(max_length=50)

    section = models.CharField(max_length=10, default="A")

    invigilator = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invigilations"
    )

    instructions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.exam.name} - {self.course.code} ({self.date} {self.start_time}-{self.end_time})"
