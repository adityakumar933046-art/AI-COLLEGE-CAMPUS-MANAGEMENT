import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

from students.models import StudentProfile
from teachers.models import TeacherProfile
from courses.models import Course


class QRSession(models.Model):

    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("CLOSED", "Closed"),
        ("EXPIRED", "Expired"),
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="qr_sessions"
    )

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="qr_sessions"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(seconds=10)

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.course.code} - {self.token}"


class QRAttendance(models.Model):

    session = models.ForeignKey(
        QRSession,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    scanned_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "session",
            "student",
        )

        ordering = [
            "-scanned_at"
        ]

    def __str__(self):
        return f"{self.student.roll_no} - {self.session.course.code}"