from django.db import models

from departments.models import Department
from courses.models import Course
from teachers.models import TeacherProfile


class Timetable(models.Model):

    DAY_CHOICES = (
        ("MONDAY", "Monday"),
        ("TUESDAY", "Tuesday"),
        ("WEDNESDAY", "Wednesday"),
        ("THURSDAY", "Thursday"),
        ("FRIDAY", "Friday"),
        ("SATURDAY", "Saturday"),
    )

    SECTION_CHOICES = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="timetables",
    )

    semester = models.PositiveIntegerField()

    section = models.CharField(
        max_length=5,
        choices=SECTION_CHOICES,
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="timetables",
    )

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="timetables",
    )

    day = models.CharField(
        max_length=20,
        choices=DAY_CHOICES,
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    classroom = models.CharField(
        max_length=100,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "day",
            "start_time",
        ]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "department",
                    "semester",
                    "section",
                    "day",
                    "start_time",
                ],
                name="unique_department_semester_section_slot",
            ),

            models.UniqueConstraint(
                fields=[
                    "teacher",
                    "day",
                    "start_time",
                ],
                name="unique_teacher_slot",
            ),

            models.UniqueConstraint(
                fields=[
                    "classroom",
                    "day",
                    "start_time",
                ],
                name="unique_classroom_slot",
            ),
        ]

    def __str__(self):

        return (
            f"{self.department.name} | "
            f"Sem {self.semester} | "
            f"Sec {self.section} | "
            f"{self.day} | "
            f"{self.course.code}"
        )