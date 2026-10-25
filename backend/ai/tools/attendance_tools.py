from attendance.models import Attendance, AttendanceSession
from students.models import StudentProfile
from django.db.models import Count, Q

def get_student_attendance(user, student_name=None):
    if user.role == "STUDENT":
        student = StudentProfile.objects.filter(user=user).first()
    else:
        if student_name:
            qs = StudentProfile.objects.all()
            for w in student_name.split():
                w = w.rstrip("'s").rstrip("'")
                qs = qs.filter(
                    Q(user__first_name__icontains=w) |
                    Q(user__last_name__icontains=w) |
                    Q(user__username__icontains=w) |
                    Q(roll_no__icontains=w)
                )
            student = qs.first()
        else:
            return {"error": "Student name is required."}

    if not student:
        return {"error": "Student not found or permission denied."}

    records = Attendance.objects.filter(student=student).select_related('session__course')
    total = records.count()
    present = records.filter(status="PRESENT").count()
    absent = records.filter(status="ABSENT").count()
    late = records.filter(status="LATE").count()

    percentage = round(((present + (late * 0.5)) / total * 100), 2) if total > 0 else 0.00

    return {
        "student": student.user.get_full_name() or student.user.username,
        "roll_no": student.roll_no,
        "total_classes": total,
        "present": present,
        "absent": absent,
        "late": late,
        "attendance_percentage": percentage
    }
