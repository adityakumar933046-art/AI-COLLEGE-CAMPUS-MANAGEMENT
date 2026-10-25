from departments.models import Department
from students.models import StudentProfile

def search_department(user, query=""):
    qs = Department.objects.all()
    if query:
        qs = qs.filter(name__icontains=query) | qs.filter(code__icontains=query)

    results = []
    for d in qs:
        st_count = StudentProfile.objects.filter(department=d).count()
        results.append({
            "id": d.id,
            "name": d.name,
            "code": d.code,
            "description": d.description or "N/A",
            "student_count": st_count
        })
    return {"count": len(results), "departments": results}
