from django.conf import settings
from django.db import models


class Department(models.Model):

    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
    )

    # ==========================
    # BASIC INFORMATION
    # ==========================

    code = models.CharField(
        max_length=20,
        unique=True,
    )

    name = models.CharField(
        max_length=150,
        unique=True,
    )

    short_name = models.CharField(
        max_length=30,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    established_year = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE",
    )

    # ==========================
    # HOD INFORMATION
    # ==========================

    hod = models.ForeignKey(
        "teachers.TeacherProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments",
    )

    hod_joining_date = models.DateField(
        null=True,
        blank=True,
    )

    # ==========================
    # CONTACT INFORMATION
    # ==========================

    office_phone = models.CharField(
        max_length=15,
        blank=True,
    )

    office_email = models.EmailField(
        blank=True,
    )

    # ==========================
    # LOCATION
    # ==========================

    building = models.CharField(
        max_length=100,
        blank=True,
    )

    # ==========================
    # DEPARTMENT LOGO
    # ==========================

    logo = models.ImageField(
        upload_to="departments/logos/",
        blank=True,
        null=True,
    )

    # ==========================
    # STATISTICS
    # ==========================

    total_faculty = models.PositiveIntegerField(
        default=0,
    )

    total_students = models.PositiveIntegerField(
        default=0,
    )

    # ==========================
    # IMPORT INFORMATION
    # ==========================

    is_imported = models.BooleanField(
        default=False,
    )

    # ==========================
    # AUDIT INFORMATION
    # ==========================

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments_updated",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def hod_name(self):
        if self.hod:
            return self.hod.full_name
        return "-"

    @property
    def is_active(self):
        return self.status == "ACTIVE"