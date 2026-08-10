from django.db import models
from django.utils import timezone

from courses.models import Course
from teachers.models import TeacherProfile
from students.models import StudentProfile


class Assignment(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    teacher = models.ForeignKey(
    TeacherProfile,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)
    file = models.FileField(
        upload_to="assignments/",
        blank=True,
        null=True
    )

    due_date = models.DateField()

    total_marks = models.PositiveIntegerField(
        default=100
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):

    STATUS_CHOICES = (

        ("PENDING", "Pending"),

        ("SUBMITTED", "Submitted"),

        ("LATE", "Late"),

    )

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to="assignment_submissions/"
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    marks = models.PositiveIntegerField(
        default=0
    )

    feedback = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    class Meta:
        unique_together = (
            "assignment",
            "student",
        )

        ordering = [
            "-submitted_at"
        ]

    def save(self, *args, **kwargs):

        if self.assignment.due_date < timezone.now().date():

            self.status = "LATE"

        else:

            self.status = "SUBMITTED"

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.student.roll_no} - {self.assignment.title}"