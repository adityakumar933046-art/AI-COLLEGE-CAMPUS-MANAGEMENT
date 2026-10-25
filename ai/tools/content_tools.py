from notes.models import Note
from announcements.models import Announcement
from assignments.models import Assignment

def search_notes(user, query=""):
    qs = Note.objects.select_related('course', 'teacher__user').all()
    if query:
        qs = qs.filter(title__icontains=query) | qs.filter(description__icontains=query)
    results = []
    for n in qs[:15]:
        results.append({
            "title": n.title,
            "course": n.course.name if n.course else "N/A",
            "teacher": n.teacher.user.get_full_name() if n.teacher else "N/A",
            "file_url": n.file.url if n.file else None
        })
    return {"count": len(results), "notes": results}

def search_announcements(user, query=""):
    qs = Announcement.objects.all()
    if user.role == "STUDENT":
        qs = qs.filter(target__in=["ALL", "STUDENT"])
    elif user.role == "TEACHER":
        qs = qs.filter(target__in=["ALL", "TEACHER"])

    if query:
        qs = qs.filter(title__icontains=query) | qs.filter(message__icontains=query)

    results = []
    for a in qs.order_by('-created_at')[:10]:
        results.append({
            "title": a.title,
            "message": a.message,
            "category": a.category,
            "priority": a.priority,
            "created_at": str(a.created_at)
        })
    return {"count": len(results), "announcements": results}

def search_assignments(user, query=""):
    qs = Assignment.objects.select_related('course').all()
    if query:
        qs = qs.filter(title__icontains=query) | qs.filter(description__icontains=query)
    results = []
    for a in qs.order_by('-due_date')[:15]:
        results.append({
            "title": a.title,
            "course": a.course.name if a.course else "N/A",
            "due_date": str(a.due_date) if a.due_date else "N/A"
        })
    return {"count": len(results), "assignments": results}
