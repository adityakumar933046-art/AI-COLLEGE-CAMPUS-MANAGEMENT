from django.conf import settings
from django.db import models

from departments.models import Department


class TeacherProfile(models.Model):

    GENDER_CHOICES = (
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    )

    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("ON_LEAVE", "On Leave"),
    )

    EMPLOYMENT_TYPE_CHOICES = (
        ("FULL_TIME", "Full Time"),
        ("PART_TIME", "Part Time"),
        ("VISITING", "Visiting Faculty"),
        ("GUEST", "Guest Faculty"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )

    employee_id = models.CharField(
        max_length=30,
        unique=True,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    designation = models.CharField(
        max_length=100,
    )

    qualification = models.CharField(
        max_length=150,
        blank=True,
    )

    specialization = models.CharField(
        max_length=150,
        blank=True,
    )

    experience = models.PositiveIntegerField(
        default=0,
        help_text="Experience in Years",
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default="FULL_TIME",
    )

    phone = models.CharField(
        max_length=15,
    )

    photo = models.ImageField(
        upload_to="teachers/",
        blank=True,
        null=True,
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )

    blood_group = models.CharField(
        max_length=5,
        blank=True,
    )

    joining_date = models.DateField(
        blank=True,
        null=True,
    )

    office_room = models.CharField(
        max_length=30,
        blank=True,
    )

    is_hod = models.BooleanField(
        default=False,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teachers_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teachers_updated",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["user__first_name", "employee_id"]
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def username(self):
        return self.user.username

    
    @property
    def experience_text(self):
        return (
            f"{self.experience} Year"
            if self.experience == 1
            else f"{self.experience} Years"
        )

    @property
    def is_active_teacher(self):
        return self.status == "ACTIVE"