from django.db import models
from django.conf import settings

from students.models import StudentProfile
from teachers.models import TeacherProfile
from courses.models import Course
from departments.models import Department


class AttendanceSession(models.Model):

    STATUS_CHOICES = (
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="attendance_sessions"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="attendance_sessions"
    )

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="attendance_sessions"
    )

    semester = models.PositiveSmallIntegerField()

    section = models.CharField(
        max_length=20,
        default="A"
    )

    lecture_no = models.PositiveSmallIntegerField()

    attendance_date = models.DateField()

    remarks = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="OPEN"
    )

    is_locked = models.BooleanField(default=False)

    locked_at = models.DateTimeField(
    null=True,
    blank=True
)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_attendance_sessions"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-attendance_date",
            "-lecture_no",
        ]

        unique_together = (
            "course",
            "attendance_date",
            "lecture_no",
            "section",
        )

    def __str__(self):
        return (
            f"{self.course.name} | "
            f"{self.attendance_date} | "
            f"Lecture {self.lecture_no}"
        )


class Attendance(models.Model):

    ATTENDANCE_STATUS = (

        ("PRESENT", "Present"),

        ("ABSENT", "Absent"),

        ("LATE", "Late"),

        ("MEDICAL", "Medical Leave"),

    )

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS,
        default="PRESENT"
    )

    remarks = models.CharField(
        max_length=255,
        blank=True
    )

    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_attendance"
    )

    marked_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "student__roll_no",
        ]

        unique_together = (
            "session",
            "student",
        )

    def __str__(self):
        return (
            f"{self.student.roll_no} - "
            f"{self.status}"
        )