from django.db import models
from django.conf import settings
from django.utils import timezone
from departments.models import Department
from courses.models import Course


class AcademicEvent(models.Model):
    CATEGORY_CHOICES = (
        ("LECTURE", "Lecture / Class Routine"),
        ("EXAM", "Examination Schedule"),
        ("ASSIGNMENT", "Assignment Deadline"),
        ("RESULT", "Result Declaration"),
        ("HOLIDAY", "Academic Holiday"),
        ("SEMINAR", "Seminar / Conference"),
        ("WORKSHOP", "Workshop / Training"),
        ("REGISTRATION", "Course Registration"),
        ("NOTICE", "Important Notice"),
        ("EVENT", "General Academic Event"),
    )

    PRIORITY_CHOICES = (
        ("NORMAL", "Normal"),
        ("IMPORTANT", "Important"),
        ("URGENT", "Urgent"),
    )

    TARGET_CHOICES = (
        ("ALL", "All Academic Users"),
        ("STUDENT", "All Students"),
        ("TEACHER", "All Teachers"),
        ("DEPARTMENT", "Specific Department"),
        ("COURSE", "Specific Course"),
    )

    STATUS_CHOICES = (
        ("DRAFT", "Draft"),
        ("PUBLISHED", "Published"),
        ("CANCELLED", "Cancelled"),
        ("ARCHIVED", "Archived"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="EVENT")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="NORMAL")
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, default="ALL")

    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="academic_events")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name="academic_events")
    semester = models.IntegerField(null=True, blank=True)

    location = models.CharField(max_length=150, blank=True, null=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PUBLISHED")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_academic_events")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time", "-priority"]

    def __str__(self):
        return f"[{self.category}] {self.title}"
