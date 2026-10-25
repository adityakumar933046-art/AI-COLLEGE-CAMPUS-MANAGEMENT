from leaves.models import Leave
from students.models import StudentProfile
from accounts.models import User

def get_leaves(user, status=None):
    if user.role == "STUDENT":
        qs = Leave.objects.filter(applicant=user)
    elif user.role == "TEACHER":
        tp = getattr(user, 'teacher_profile', None)
        if tp and tp.department:
            student_users = User.objects.filter(role="STUDENT", student_profile__department=tp.department)
            qs = Leave.objects.filter(applicant__in=student_users)
        else:
            qs = Leave.objects.none()
    else:
        qs = Leave.objects.all()

    if status:
        qs = qs.filter(status__iexact=status)

    qs = qs.select_related('applicant').order_by('-applied_at')[:20]

    items = []
    for l in qs:
        items.append({
            "id": l.id,
            "applicant": l.applicant.get_full_name() or l.applicant.username,
            "leave_type": l.leave_type,
            "from_date": str(l.from_date),
            "to_date": str(l.to_date),
            "reason": l.reason,
            "status": l.status,
            "remarks": l.remarks or "N/A"
        })
    return {"count": len(items), "leaves": items}
