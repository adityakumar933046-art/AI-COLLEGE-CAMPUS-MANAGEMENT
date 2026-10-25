from timetable.models import Timetable
from students.models import StudentProfile

def get_timetable(user, day=None):
    qs = Timetable.objects.select_related('department', 'course', 'teacher__user').all()
    if user.role == "STUDENT":
        sp = getattr(user, 'student_profile', None)
        if sp and sp.department:
            qs = qs.filter(department=sp.department)
    elif user.role == "TEACHER":
        tp = getattr(user, 'teacher_profile', None)
        if tp:
            qs = qs.filter(teacher=tp)

    if day:
        qs = qs.filter(day__iexact=day)

    items = []
    for t in qs[:15]:
        items.append({
            "day": t.day,
            "course": t.course.name if t.course else "N/A",
            "course_code": t.course.code if t.course else "N/A",
            "teacher": t.teacher.user.get_full_name() if t.teacher else "N/A",
            "time": f"{t.start_time} - {t.end_time}",
            "classroom": t.classroom
        })
    return {"count": len(items), "timetable": items}
