from django.db import models
from courses.models import Course
from teachers.models import TeacherProfile


class Note(models.Model):
    MATERIAL_TYPES = (
        ("LECTURE_NOTES", "Lecture Notes"),
        ("STUDY_NOTES", "Study Notes"),
        ("PDF", "PDF Document"),
        ("PRESENTATION", "Presentation Slide (PPT/PPTX)"),
        ("QUESTION_PAPER", "Question Paper / Sample Paper"),
        ("ASSIGNMENT_MATERIAL", "Assignment Reference Material"),
        ("REFERENCE", "Reference Reading"),
        ("SYLLABUS", "Course Syllabus"),
        ("LAB_MATERIAL", "Lab Manual / Lab Notes"),
        ("OTHER", "Other Academic Material"),
    )

    STATUS_CHOICES = (
        ("PUBLISHED", "Published"),
        ("ARCHIVED", "Archived"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="notes")
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="notes")
    
    unit_topic = models.CharField(max_length=150, blank=True, null=True)
    material_type = models.CharField(max_length=30, choices=MATERIAL_TYPES, default="LECTURE_NOTES")
    
    file = models.FileField(upload_to="notes/")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PUBLISHED")
    download_count = models.IntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"[{self.course.code}] {self.title}"
