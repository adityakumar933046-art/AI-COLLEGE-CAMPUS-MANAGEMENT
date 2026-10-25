from students.models import StudentProfile
from django.db.models import Q

def search_student(user, query="", department_id=None, semester=None):
    if user.role == "STUDENT":
        qs = StudentProfile.objects.filter(user=user)
    elif user.role == "TEACHER":
        tp = getattr(user, 'teacher_profile', None)
        if tp and tp.department:
            qs = StudentProfile.objects.filter(department=tp.department)
        else:
            qs = StudentProfile.objects.none()
    else:
        qs = StudentProfile.objects.all()

    if query:
        words = query.split()
        for w in words:
            qs = qs.filter(
                Q(user__first_name__icontains=w) |
                Q(user__last_name__icontains=w) |
                Q(user__username__icontains=w) |
                Q(roll_no__icontains=w) |
                Q(admission_no__icontains=w)
            )
    if department_id:
        qs = qs.filter(department_id=department_id)
    if semester:
        qs = qs.filter(semester=semester)

    qs = qs.select_related('user', 'department')[:20]
    
    results = []
    for s in qs:
        results.append({
            "id": s.id,
            "full_name": s.user.get_full_name() or s.user.username,
            "username": s.user.username,
            "roll_no": s.roll_no,
            "admission_no": s.admission_no,
            "department": s.department.name if s.department else "N/A",
            "semester": s.semester,
            "section": s.section,
            "cgpa": str(s.cgpa) if s.cgpa else "N/A",
            "status": s.status
        })
    return {"count": len(results), "students": results}

def get_student_profile(user, student_id=None, student_name=None):
    if user.role == "STUDENT":
        s = StudentProfile.objects.filter(user=user).select_related('user', 'department').first()
    else:
        qs = StudentProfile.objects.all()
        if user.role == "TEACHER":
            tp = getattr(user, 'teacher_profile', None)
            if tp and tp.department:
                qs = qs.filter(department=tp.department)
            else:
                qs = qs.none()

        if student_id:
            s = qs.filter(id=student_id).select_related('user', 'department').first()
        elif student_name:
            s = qs.filter(
                Q(user__first_name__icontains=student_name) |
                Q(user__last_name__icontains=student_name) |
                Q(user__username__icontains=student_name) |
                Q(roll_no__icontains=student_name)
            ).select_related('user', 'department').first()
        else:
            s = None

    if not s:
        return {"error": "Student profile not found or permission denied."}

    return {
        "id": s.id,
        "full_name": s.user.get_full_name() or s.user.username,
        "username": s.user.username,
        "email": s.user.email if user.role in ["ADMIN", "TEACHER"] or user == s.user else "[Hidden]",
        "roll_no": s.roll_no,
        "admission_no": s.admission_no,
        "department": s.department.name if s.department else "N/A",
        "semester": s.semester,
        "section": s.section,
        "batch": s.batch,
        "phone": s.phone if user.role in ["ADMIN", "TEACHER"] or user == s.user else "[Hidden]",
        "city": s.city,
        "state": s.state,
        "cgpa": str(s.cgpa) if s.cgpa else "N/A",
        "status": s.status
    }
