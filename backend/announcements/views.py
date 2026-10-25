def clean_query_param(val):
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str.lower() in ("", "none", "null", "undefined"):
        return None
    return val_str

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from accounts.decorators import admin_required, admin_or_teacher_required
from students.models import StudentProfile
from teachers.models import TeacherProfile

from .models import Announcement, AnnouncementRead
from .forms import AnnouncementForm


# ==========================================
# ANNOUNCEMENT LIST
# ==========================================
@login_required
def announcement_list(request):
    user = request.user
    now = timezone.now()

    # Base Queryset
    if user.role == "ADMIN":
        announcements = Announcement.objects.select_related("created_by", "department", "course").all()
    else:
        # Published & Time-Valid
        announcements = Announcement.objects.select_related("created_by", "department", "course").filter(
            status="PUBLISHED",
            publish_at__lte=now
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gte=now)
        )

        if user.role == "STUDENT":
            try:
                student = StudentProfile.objects.filter(user=user).first()
                announcements = announcements.filter(
                    Q(target__in=["ALL", "STUDENT"]) |
                    Q(target="DEPARTMENT", department=student.department) |
                    Q(target="COURSE", course__department=student.department, course__semester=student.semester)
                )
            except StudentProfile.DoesNotExist:
                announcements = announcements.filter(target="ALL")

        elif user.role == "TEACHER":
            try:
                teacher = TeacherProfile.objects.filter(user=user).first()
                announcements = announcements.filter(
                    Q(target__in=["ALL", "TEACHER"]) |
                    Q(target="DEPARTMENT", department=teacher.department) |
                    Q(target="COURSE", course__teacher=teacher) |
                    Q(created_by=user)
                )
            except TeacherProfile.DoesNotExist:
                announcements = announcements.filter(target="ALL")

    # Search Filter
    search = clean_query_param(request.GET.get("search"))
    if search:
        announcements = announcements.filter(
            Q(title__icontains=search) |
            Q(message__icontains=search) |
            Q(category__icontains=search) |
            Q(created_by__first_name__icontains=search) |
            Q(created_by__last_name__icontains=search)
        )

    category = clean_query_param(request.GET.get("category"))
    if category:
        announcements = announcements.filter(category=category)

    priority = clean_query_param(request.GET.get("priority"))
    if priority:
        announcements = announcements.filter(priority=priority)

    announcements = announcements.distinct().order_by("-is_pinned", "-created_at")

    # Get Read IDs for user
    read_ids = set(AnnouncementRead.objects.filter(user=user).values_list("announcement_id", flat=True))

    paginator = Paginator(announcements, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "announcements": page_obj,
        "page_obj": page_obj,
        "search": search,
        "category": category,
        "priority": priority,
        "read_ids": read_ids,
    }
    return render(request, "announcements/announcement_list.html", context)


# ==========================================
# ANNOUNCEMENT DETAIL
# ==========================================
@login_required
def announcement_detail(request, pk):
    announcement = get_object_or_404(Announcement.objects.select_related("created_by", "department", "course"), pk=pk)

    # Mark Read for user
    AnnouncementRead.objects.get_or_create(announcement=announcement, user=request.user)

    return render(request, "announcements/announcement_detail.html", {"announcement": announcement})


# ==========================================
# CREATE ANNOUNCEMENT
# ==========================================
@login_required
@admin_or_teacher_required
def announcement_create(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, "Academic notice created successfully.")
            return redirect("announcement_list")
    else:
        form = AnnouncementForm()

    return render(request, "announcements/announcement_create.html", {"form": form})


# ==========================================
# UPDATE ANNOUNCEMENT
# ==========================================
@login_required
@admin_or_teacher_required
def announcement_update(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.user.role == "TEACHER" and announcement.created_by != request.user:
        messages.error(request, "You can only edit announcements created by you.")
        return redirect("announcement_list")

    if request.method == "POST":
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, "Announcement updated successfully.")
            return redirect("announcement_detail", pk=announcement.pk)
    else:
        form = AnnouncementForm(instance=announcement)

    return render(request, "announcements/announcement_update.html", {"form": form, "announcement": announcement})


# ==========================================
# DELETE ANNOUNCEMENT
# ==========================================
@login_required
@admin_or_teacher_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.user.role == "TEACHER" and announcement.created_by != request.user:
        messages.error(request, "You can only delete announcements created by you.")
        return redirect("announcement_list")

    if request.method == "POST":
        announcement.delete()
        messages.success(request, "Announcement deleted successfully.")
        return redirect("announcement_list")

    return render(request, "announcements/announcement_delete.html", {"announcement": announcement})


# ==========================================
# MY ANNOUNCEMENTS & PUBLIC
# ==========================================
@login_required
def my_announcements(request):
    return redirect("announcement_list")

@login_required
def public_announcements(request):
    return redirect("announcement_list")


# ==========================================
# MARK NOTIFICATION READ & MARK ALL READ
# ==========================================
@login_required
def mark_as_read(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    AnnouncementRead.objects.get_or_create(announcement=announcement, user=request.user)
    messages.success(request, "Notification marked as read.")
    return redirect(request.META.get("HTTP_REFERER", "announcement_list"))


@login_required
def mark_all_as_read(request):
    user = request.user
    now = timezone.now()
    qs = Announcement.objects.filter(status="PUBLISHED", publish_at__lte=now)
    for ann in qs:
        AnnouncementRead.objects.get_or_create(announcement=ann, user=user)
    messages.success(request, "All notifications marked as read.")
    return redirect(request.META.get("HTTP_REFERER", "announcement_list"))
