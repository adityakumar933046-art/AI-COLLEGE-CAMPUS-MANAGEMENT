from teachers.models import TeacherProfile
from django.db.models import Q

def search_teacher(user, query="", department_id=None):
    qs = TeacherProfile.objects.select_related('user', 'department').all()
    if query:
        qs = qs.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(employee_id__icontains=query)
        )
    if department_id:
        qs = qs.filter(department_id=department_id)

    results = []
    for t in qs[:20]:
        results.append({
            "id": t.id,
            "full_name": t.user.get_full_name() or t.user.username,
            "employee_id": t.employee_id,
            "department": t.department.name if t.department else "N/A",
            "designation": t.designation,
            "status": t.status
        })
    return {"count": len(results), "teachers": results}

def get_teacher_profile(user, teacher_id=None, teacher_name=None):
    qs = TeacherProfile.objects.select_related('user', 'department').all()
    if teacher_id:
        t = qs.filter(id=teacher_id).first()
    elif teacher_name:
        t = qs.filter(
            Q(user__first_name__icontains=teacher_name) |
            Q(user__last_name__icontains=teacher_name) |
            Q(employee_id__icontains=teacher_name)
        ).first()
    else:
        t = None

    if not t:
        return {"error": "Teacher profile not found."}

    return {
        "id": t.id,
        "full_name": t.user.get_full_name() or t.user.username,
        "employee_id": t.employee_id,
        "department": t.department.name if t.department else "N/A",
        "designation": t.designation,
        "qualification": t.qualification,
        "experience_years": t.experience_years,
        "joining_date": str(t.joining_date) if t.joining_date else "N/A"
    }
