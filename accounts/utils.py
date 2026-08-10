from students.models import StudentProfile
from teachers.models import TeacherProfile
from courses.models import Course


def dashboard_counts():

    return {

        "students_count":

        StudentProfile.objects.count(),

        "teachers_count":

        TeacherProfile.objects.count(),

        "courses_count":

        Course.objects.count(),

    }