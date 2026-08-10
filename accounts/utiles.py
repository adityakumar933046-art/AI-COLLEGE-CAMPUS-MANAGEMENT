from students.models import StudentProfile
from teachers.models import TeacherProfile
from courses.models import Course
from assignments.models import Assignment
from attendance.models import Attendance


def dashboard_counts():

    return {

        "students_count": StudentProfile.objects.count(),

        "teachers_count": TeacherProfile.objects.count(),

        "courses_count": Course.objects.count(),

        "assignments_count": Assignment.objects.count(),

        "attendance_count": Attendance.objects.count(),

    }

