from django.db import models
from django.conf import settings


class StudentProfile(models.Model):

    GENDER_CHOICES = (
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    )


    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("GRADUATED", "Graduated"),
    )


    # ==========================
    # ACCOUNT INFORMATION
    # ==========================

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )


    # ==========================
    # ACADEMIC INFORMATION
    # ==========================
    admission_no = models.CharField(
    max_length=30,
    unique=True,
    null=True,
    blank=True,
    db_index=True,
)


    roll_no = models.CharField(
    max_length=20,
    unique=True,
    null=True,
    blank=True,
    db_index=True,
)


    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )


    semester = models.PositiveIntegerField()


    section = models.CharField(
        max_length=10,
        blank=True,
    )


    batch = models.CharField(
        max_length=20,
        blank=True,
    )


    academic_year = models.CharField(
        max_length=20,
        blank=True,
    )


    admission_date = models.DateField(
        null=True,
        blank=True,
    )


    # ==========================
    # PERSONAL INFORMATION
    # ==========================

    photo = models.ImageField(
        upload_to="students/photos/",
        null=True,
        blank=True,
    )


    phone = models.CharField(
        max_length=15,
        blank=True,
    )


    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
    )


    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )


    blood_group = models.CharField(
        max_length=5,
        blank=True,
    )


    # ==========================
    # GUARDIAN INFORMATION
    # ==========================

    father_name = models.CharField(
        max_length=100,
        blank=True,
    )


    mother_name = models.CharField(
        max_length=100,
        blank=True,
    )


    guardian_phone = models.CharField(
        max_length=15,
        blank=True,
    )


    # ==========================
    # ADDRESS INFORMATION
    # ==========================

    address = models.TextField(
        blank=True,
    )


    city = models.CharField(
        max_length=100,
        blank=True,
    )


    state = models.CharField(
        max_length=100,
        blank=True,
    )


    pincode = models.CharField(
        max_length=10,
        blank=True,
    )


    # ==========================
    # ACADEMIC PERFORMANCE
    # ==========================

    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00,
    )


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE",
    )


    # ==========================
    # IMPORT INFORMATION
    # ==========================

    is_imported = models.BooleanField(
        default=False,
    )


    # ==========================
    # SYSTEM INFORMATION
    # ==========================

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students_created",
    )


    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students_updated",
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    updated_at = models.DateTimeField(
        auto_now=True,
    )


    class Meta:

        ordering = [
            "roll_no"
        ]

        verbose_name = "Student"

        verbose_name_plural = "Students"



    def __str__(self):

        return f"{self.roll_no} - {self.user.get_full_name()}"


    @property
    def full_name(self):

        return self.user.get_full_name()


    @property
    def email(self):

        return self.user.email


    @property
    def profile_photo(self):

        if self.photo:
            return self.photo.url

        return None