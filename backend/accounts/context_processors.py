from django.db.models import Q
from django.utils import timezone
from announcements.models import Announcement, AnnouncementRead
from students.models import StudentProfile
from teachers.models import TeacherProfile


def global_data(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user
        now = timezone.now()

        # Target-scoped published announcements
        qs = Announcement.objects.filter(
            status="PUBLISHED",
            publish_at__lte=now
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gte=now)
        )

        if user.role == "ADMIN":
            pass
        elif user.role == "STUDENT":
            try:
                student = StudentProfile.objects.get(user=user)
                qs = qs.filter(
                    Q(target__in=["ALL", "STUDENT"]) |
                    Q(target="DEPARTMENT", department=student.department) |
                    Q(target="COURSE", course__department=student.department, course__semester=student.semester)
                )
            except StudentProfile.DoesNotExist:
                qs = qs.filter(target="ALL")
        elif user.role == "TEACHER":
            try:
                teacher = TeacherProfile.objects.get(user=user)
                qs = qs.filter(
                    Q(target__in=["ALL", "TEACHER"]) |
                    Q(target="DEPARTMENT", department=teacher.department) |
                    Q(target="COURSE", course__teacher=teacher) |
                    Q(created_by=user)
                )
            except TeacherProfile.DoesNotExist:
                qs = qs.filter(target="ALL")

        # Exclude read items
        read_ids = AnnouncementRead.objects.filter(user=user).values_list("announcement_id", flat=True)
        unread_qs = qs.exclude(id__in=read_ids).distinct().order_by("-is_pinned", "-created_at")

        unread_count = unread_qs.count()
        recent_notifications = unread_qs[:5]

        context["notifications"] = recent_notifications
        context["notifications_count"] = unread_count
        context["notification_count"] = unread_count
    else:
        context["notifications"] = []
        context["notifications_count"] = 0
        context["notification_count"] = 0

    return context
