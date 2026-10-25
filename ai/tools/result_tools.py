from results.models import Result
from students.models import StudentProfile
from django.db.models import Q

def get_student_results(user, student_name=None):
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
        return {"error": "Student record not found or permission denied."}

    res_qs = Result.objects.filter(student=student).select_related('course')
    items = []
    for r in res_qs:
        items.append({
            "course": r.course.name if r.course else "N/A",
            "course_code": r.course.code if r.course else "N/A",
            "marks": str(r.marks),
            "grade": r.grade,
            "exam_type": r.exam_type
        })

    return {
        "student": student.user.get_full_name() or student.user.username,
        "roll_no": student.roll_no,
        "cgpa": str(student.cgpa) if student.cgpa else "N/A",
        "results_count": len(items),
        "results": items
    }
