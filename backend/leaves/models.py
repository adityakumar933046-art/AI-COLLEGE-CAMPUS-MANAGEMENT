from django.db import models
from django.conf import settings


class Leave(models.Model):

    LEAVE_TYPE_CHOICES = (
        ("MEDICAL", "Medical Leave"),
        ("ACADEMIC", "Academic Leave"),
        ("OTHER", "Other"),
    )

    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
    )

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leaves"
    )

    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_TYPE_CHOICES,
        default="MEDICAL"
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

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_leaves"
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
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.applicant.username} - {self.leave_type} ({self.status})"
