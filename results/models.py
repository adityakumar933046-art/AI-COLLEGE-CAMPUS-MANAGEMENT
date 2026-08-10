from django.db import models
from students.models import StudentProfile
from teachers.models import TeacherProfile
from courses.models import Course


class Result(models.Model):
    EXAM_TYPE_CHOICES = (
        ("Mid Semester", "Mid Semester"),
        ("End Semester", "End Semester"),
        ("Internal Assessment", "Internal Assessment"),
        ("Quiz / Test", "Quiz / Test"),
        ("Practical", "Practical"),
    )

    GRADE_CHOICES = (
        ("A+", "A+"),
        ("A", "A"),
        ("B+", "B+"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("F", "Fail"),
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="results"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="results"
    )

    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="results"
    )

    exam_type = models.CharField(
        max_length=50,
        choices=EXAM_TYPE_CHOICES,
        default="End Semester"
    )

    semester = models.PositiveIntegerField()

    marks_obtained = models.PositiveIntegerField()

    total_marks = models.PositiveIntegerField(
        default=100
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        editable=False
    )

    grade = models.CharField(
        max_length=5,
        choices=GRADE_CHOICES
    )

    is_published = models.BooleanField(
        default=True
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = (
            "student",
            "course",
            "semester",
            "exam_type",
        )
        ordering = [
            "-semester",
            "course__name",
        ]

    def save(self, *args, **kwargs):
        if self.total_marks > 0:
            self.percentage = (self.marks_obtained / self.total_marks) * 100
        else:
            self.percentage = 0

        p = self.percentage
        if p >= 90:
            self.grade = "A+"
        elif p >= 80:
            self.grade = "A"
        elif p >= 70:
            self.grade = "B+"
        elif p >= 60:
            self.grade = "B"
        elif p >= 50:
            self.grade = "C"
        elif p >= 40:
            self.grade = "D"
        else:
            self.grade = "F"

        super().save(*args, **kwargs)

    @property
    def grade_point(self):
        g = self.grade
        if g == "A+": return 10.0
        elif g == "A": return 9.0
        elif g == "B+": return 8.0
        elif g == "B": return 7.0
        elif g == "C": return 6.0
        elif g == "D": return 5.0
        else: return 0.0

    def __str__(self):
        return f"{self.student.roll_no} - {self.course.code} ({self.exam_type})"
