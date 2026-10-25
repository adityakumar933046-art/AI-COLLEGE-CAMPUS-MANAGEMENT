from courses.models import Course
from django.db.models import Q

def search_course(user, query="", department_id=None):
    qs = Course.objects.select_related('department', 'teacher__user').all()
    if user.role == "TEACHER" and hasattr(user, 'teacher_profile'):
        qs = qs.filter(teacher=user.teacher_profile)

    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(code__icontains=query))
    if department_id:
        qs = qs.filter(department_id=department_id)

    results = []
    for c in qs[:20]:
        results.append({
            "id": c.id,
            "code": c.code,
            "name": c.name,
            "department": c.department.name if c.department else "N/A",
            "teacher": c.teacher.user.get_full_name() if c.teacher else "Unassigned",
            "credits": c.credits,
            "semester": c.semester
        })
    return {"count": len(results), "courses": results}
