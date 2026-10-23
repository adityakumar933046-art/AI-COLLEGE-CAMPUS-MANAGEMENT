from datetime import date, timedelta

from django.db.models import Count, Q

from .models import Attendance, AttendanceSession
from students.models import StudentProfile


class AttendanceService:
    """
    Business logic for Attendance Module
    """

    # ==========================
    # Student Attendance
    # ==========================

    @staticmethod
    def get_student_summary(student):

        total = Attendance.objects.filter(
            student=student
        ).count()

        present = Attendance.objects.filter(
            student=student,
            status="PRESENT"
        ).count()

        absent = Attendance.objects.filter(
            student=student,
            status="ABSENT"
        ).count()

        late = Attendance.objects.filter(
            student=student,
            status="LATE"
        ).count()

        medical = Attendance.objects.filter(
            student=student,
            status="MEDICAL"
        ).count()

        percentage = round(
            (present / total) * 100,
            2
        ) if total else 0

        return {
            "total": total,
            "present": present,
            "absent": absent,
            "late": late,
            "medical": medical,
            "percentage": percentage,
        }

    # ==========================
    # Course Attendance
    # ==========================

    @staticmethod
    def get_course_summary(course):

        attendance = Attendance.objects.filter(
            session__course=course
        )

        total = attendance.count()

        present = attendance.filter(
            status="PRESENT"
        ).count()

        absent = attendance.filter(
            status="ABSENT"
        ).count()

        late = attendance.filter(
            status="LATE"
        ).count()

        medical = attendance.filter(
            status="MEDICAL"
        ).count()

        percentage = round(
            (present / total) * 100,
            2
        ) if total else 0

        return {
            "total": total,
            "present": present,
            "absent": absent,
            "late": late,
            "medical": medical,
            "percentage": percentage,
        }

    # ==========================
    # Department Attendance
    # ==========================

    @staticmethod
    def get_department_summary(department):

        attendance = Attendance.objects.filter(
            session__department=department
        )

        total = attendance.count()

        present = attendance.filter(
            status="PRESENT"
        ).count()

        absent = attendance.filter(
            status="ABSENT"
        ).count()

        percentage = round(
            (present / total) * 100,
            2
        ) if total else 0

        return {
            "total": total,
            "present": present,
            "absent": absent,
            "percentage": percentage,
        }

    # ==========================
    # Dashboard Statistics
    # ==========================

    @staticmethod
    def dashboard_statistics():

        today = date.today()

        today_attendance = Attendance.objects.filter(
            session__attendance_date=today , status = "PRESENT"
        )

        total_students = StudentProfile.objects.count()

        present_today = today_attendance.filter(
            status="PRESENT"
        ).count()

        absent_today = today_attendance.filter(
            status="ABSENT"
        ).count()

        late_today = today_attendance.filter(
            status="LATE"
        ).count()

        medical_today = today_attendance.filter(
            status="MEDICAL"
        ).count()

        total_today = today_attendance.count()

        overall_percentage = round(
            (present_today / total_today) * 100,
            2
        ) if total_today else 0

        return {
            "total_students": total_students,
            "present_today": present_today,
            "absent_today": absent_today,
            "late_today": late_today,
            "medical_today": medical_today,
            "overall_percentage": overall_percentage,
        }

    # ==========================
    # Defaulters
    # ==========================

    @staticmethod
    def get_defaulters(min_percentage=75):

        students = StudentProfile.objects.select_related("user")

        defaulters = []

        for student in students:

            summary = AttendanceService.get_student_summary(student)

            if summary["percentage"] < min_percentage:

                student.attendance_percentage = summary["percentage"]
                student.total_classes = summary["total"]
                student.present_classes = summary["present"]

                defaulters.append(student)

        return sorted(
            defaulters,
            key=lambda x: x.attendance_percentage
        )

    # ==========================
    # Monthly Attendance
    # ==========================

    @staticmethod
    def monthly_statistics():

        result = []

        today = date.today()

        for i in range(5, -1, -1):

            month = today.month - i

            year = today.year

            if month <= 0:
                month += 12
                year -= 1

            attendance = Attendance.objects.filter(
                session__attendance_date__year=year,
                session__attendance_date__month=month
            )

            total = attendance.count()

            present = attendance.filter(
                status="PRESENT"
            ).count()

            percentage = round(
                (present / total) * 100,
                2
            ) if total else 0

            result.append({
                "month": month,
                "year": year,
                "percentage": percentage,
            })

        return result

    # ==========================
    # Recent Sessions
    # ==========================

    @staticmethod
    def recent_sessions(limit=10):

        return AttendanceSession.objects.select_related(
            "course",
            "teacher",
            "department"
        ).order_by(
            "-attendance_date",
            "-created_at"
        )[:limit]

    # ==========================
    # Top Students
    # ==========================

    @staticmethod
    def top_students(limit=10):

        students = StudentProfile.objects.select_related("user")

        ranking = []

        for student in students:

            summary = AttendanceService.get_student_summary(student)

            student.attendance_percentage = summary["percentage"]

            ranking.append(student)

        ranking.sort(
            key=lambda x: x.attendance_percentage,
            reverse=True
        )

        return ranking[:limit]

    # ==========================
    # Low Attendance Students
    # ==========================

    @staticmethod
    def low_attendance_students(limit=10):

        students = AttendanceService.top_students(100000)

        students.sort(
            key=lambda x: x.attendance_percentage
        )

        return students[:limit]