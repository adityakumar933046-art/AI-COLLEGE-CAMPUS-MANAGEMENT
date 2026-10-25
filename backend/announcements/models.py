from django.db import models
from django.conf import settings
from django.utils import timezone
from departments.models import Department
from courses.models import Course


class Announcement(models.Model):

    CATEGORY_CHOICES = (
        ("ACADEMIC", "Academic Notice"),
        ("EXAM", "Examination"),
        ("ASSIGNMENT", "Assignment"),
        ("ATTENDANCE", "Attendance"),
        ("TIMETABLE", "Timetable Change"),
        ("RESULT", "Result Declaration"),
        ("COURSE", "Course Update"),
        ("DEPARTMENT", "Department Notice"),
        ("NOTICE", "General Notice"),
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
        ("SCHEDULED", "Scheduled"),
        ("PUBLISHED", "Published"),
        ("EXPIRED", "Expired"),
    )

    title = models.CharField(max_length=200)
    message = models.TextField()
    
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="ACADEMIC")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="NORMAL")
    target = models.CharField(max_length=20, choices=TARGET_CHOICES, default="ALL")
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="announcements")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name="announcements")
    semester = models.IntegerField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PUBLISHED")
    publish_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    attachment = models.FileField(upload_to="announcements/attachments/", null=True, blank=True)
    is_pinned = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="announcements"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return f"[{self.category}] {self.title}"

    @property
    def is_visible(self):
        now = timezone.now()
        if self.status != "PUBLISHED":
            return False
        if self.publish_at and self.publish_at > now:
            return False
        if self.expires_at and self.expires_at < now:
            return False
        return True


class AnnouncementRead(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name="read_records")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="announcement_reads")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("announcement", "user")

    def __str__(self):
        return f"{self.user.username} read {self.announcement.title}"
