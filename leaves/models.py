from django.db import models
from django.conf import settings


class Leave(models.Model):

    STATUS_CHOICES = (

        ("PENDING", "Pending"),

        ("APPROVED", "Approved"),

        ("REJECTED", "Rejected"),

    )

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leaves"
    )

    from_date = models.DateField()

    to_date = models.DateField()

    reason = models.TextField()

    medical_certificate = models.FileField(
        upload_to="leave_certificates/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    remarks = models.TextField(
        blank=True
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "-applied_at"
        ]

    def __str__(self):

        return f"{self.applicant.username} - {self.status}"