from django.db import models
from django.conf import settings

from departments.models import Department
from teachers.models import TeacherProfile


class Course(models.Model):

    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
    )

    code = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=150
    )

    description = models.TextField(
        blank=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses"
    )

    semester = models.PositiveSmallIntegerField()

    credits = models.PositiveSmallIntegerField(default=4)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    # ===== Import Information =====

    imported_from_excel = models.BooleanField(
        default=False
    )

    import_batch = models.CharField(
        max_length=100,
        blank=True
    )

    # ===== Audit =====

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_courses"
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_courses"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["semester", "name"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return f"{self.code} - {self.name}"


class CourseMaterial(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="materials"
    )

    title = models.CharField(
        max_length=200
    )

    file = models.FileField(
        upload_to="course_materials/"
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.course.name} - {self.title}"