def clean_query_param(val):
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str.lower() in ("", "none", "null", "undefined"):
        return None
    return val_str

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from accounts.decorators import admin_required, admin_or_teacher_required
from students.models import StudentProfile
from teachers.models import TeacherProfile
from departments.models import Department
from courses.models import Course
from attendance.models import Attendance
from announcements.models import Announcement
from assignments.models import Assignment
from results.models import Result
from notes.models import Note
from timetable.models import Timetable
from leaves.models import Leave

from .models import AcademicEvent
from .forms import AcademicEventForm


# ==========================================================
# DASHBOARD REDIRECT
# ==========================================================
@login_required
def dashboard_redirect(request):
    user = request.user
    if user.role == "ADMIN":
        return redirect("admin_dashboard")
    elif user.role == "TEACHER":
        return redirect("teacher_dashboard")
    elif user.role == "STUDENT":
        return redirect("student_dashboard")
    return redirect("login")


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================
@login_required
def admin_dashboard(request):
    today = timezone.now().date()

    total_students = StudentProfile.objects.count()
    total_teachers = TeacherProfile.objects.count()
    total_departments = Department.objects.count()
    total_courses = Course.objects.count()

    active_students = StudentProfile.objects.filter(status="ACTIVE").count()
    active_teachers = TeacherProfile.objects.filter(status="ACTIVE").count()
    active_courses = Course.objects.filter(status="ACTIVE").count()

    today_attendance = Attendance.objects.filter(session__attendance_date=today).count()
    present_today = Attendance.objects.filter(session__attendance_date=today, status="PRESENT").count()
    absent_today = Attendance.objects.filter(session__attendance_date=today, status="ABSENT").count()

    context = {
        "total_students": total_students,
        "active_students": active_students,
        "total_teachers": total_teachers,
        "active_teachers": active_teachers,
        "total_departments": total_departments,
        "total_courses": total_courses,
        "active_courses": active_courses,
        "today_attendance": today_attendance,
        "present_today": present_today,
        "absent_today": absent_today,
    }
    return render(request, "dashboard/admin_dashboard.html", context)


# ==========================================================
# TEACHER DASHBOARD
# ==========================================================
@login_required
def teacher_dashboard(request):
    try:
        teacher = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        return redirect("admin_dashboard")

    assigned_courses = Course.objects.filter(teacher=teacher)
    today_schedule = Timetable.objects.filter(teacher=teacher)

    context = {
        "teacher": teacher,
        "assigned_courses": assigned_courses,
        "today_schedule": today_schedule,
    }
    return render(request, "dashboard/teacher_dashboard.html", context)


# ==========================================================
# STUDENT DASHBOARD
# ==========================================================
@login_required
def student_dashboard(request):
    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return redirect("admin_dashboard")

    enrolled_courses = Course.objects.filter(department=student.department, semester=student.semester)

    context = {
        "student": student,
        "enrolled_courses": enrolled_courses,
    }
    return render(request, "dashboard/student_dashboard.html", context)


# ==========================================================
# REAL ROLE-AWARE ANALYTICS API ENDPOINT
# ==========================================================
@login_required
def analytics_api(request):
    user = request.user

    if user.role == "ADMIN":
        today = timezone.now().date()
        past_days = [(today - timezone.timedelta(days=i)) for i in range(6, -1, -1)]
        day_labels = [d.strftime("%a %d") for d in past_days]
        attendance_trend = []
        for d in past_days:
            tot = Attendance.objects.filter(session__attendance_date=d).count()
            prs = Attendance.objects.filter(session__attendance_date=d, status="PRESENT").count()
            pct = round((prs / tot) * 100, 1) if tot > 0 else 0.0
            attendance_trend.append(pct)

        dept_labels = []
        dept_data = []
        for d in Department.objects.annotate(std_cnt=Count("students")):
            dept_labels.append(d.short_name or d.name)
            dept_data.append(d.std_cnt)

        grade_labels = ["A+", "A", "B+", "B", "C", "D", "F"]
        grade_data = [
            Result.objects.filter(grade="A+").count(),
            Result.objects.filter(grade="A").count(),
            Result.objects.filter(grade="B+").count(),
            Result.objects.filter(grade="B").count(),
            Result.objects.filter(grade="C").count(),
            Result.objects.filter(grade="D").count(),
            Result.objects.filter(grade="F").count(),
        ]

        defaulters = []
        for s in StudentProfile.objects.select_related("department", "user")[:15]:
            tot = Attendance.objects.filter(student=s).count()
            prs = Attendance.objects.filter(student=s, status="PRESENT").count()
            pct = round((prs / tot) * 100, 1) if tot > 0 else 0.0
            if pct < 75.0:
                defaulters.append({
                    "name": s.full_name,
                    "roll_no": s.roll_no,
                    "department": s.department.short_name if s.department else "N/A",
                    "attendance_pct": pct
                })

        return JsonResponse({
            "role": "ADMIN",
            "attendance_trend": {"labels": day_labels, "data": attendance_trend},
            "dept_distribution": {"labels": dept_labels, "data": dept_data},
            "grade_distribution": {"labels": grade_labels, "data": grade_data},
            "defaulters": defaulters,
        })

    elif user.role == "TEACHER":
        teacher = get_object_or_404(TeacherProfile, user=user)
        courses = Course.objects.filter(teacher=teacher)
        course_labels = []
        course_attendance = []
        for c in courses:
            tot = Attendance.objects.filter(session__course=c).count()
            prs = Attendance.objects.filter(session__course=c, status="PRESENT").count()
            pct = round((prs / tot) * 100, 1) if tot > 0 else 0.0
            course_labels.append(c.code)
            course_attendance.append(pct)

        return JsonResponse({
            "role": "TEACHER",
            "course_attendance": {"labels": course_labels, "data": course_attendance},
        })

    else:
        student = get_object_or_404(StudentProfile, user=user)
        records = Attendance.objects.filter(student=student)
        subject_labels = []
        subject_attendance = []
        for c in Course.objects.filter(department=student.department, semester=student.semester):
            tot = records.filter(session__course=c).count()
            prs = records.filter(session__course=c, status="PRESENT").count()
            pct = round((prs / tot) * 100, 1) if tot > 0 else 0.0
            subject_labels.append(c.code)
            subject_attendance.append(pct)

        return JsonResponse({
            "role": "STUDENT",
            "subject_attendance": {"labels": subject_labels, "data": subject_attendance},
        })


# ==========================================================
# ADVANCED INTEGRATED ACADEMIC CALENDAR VIEW & CRUD
# ==========================================================
@login_required
def dashboard_calendar(request):
    user = request.user
    today = timezone.now().date()
    now = timezone.now()

    # 1. Custom Academic Events
    custom_events_qs = AcademicEvent.objects.select_related("created_by", "department", "course").all()
    if user.role != "ADMIN":
        custom_events_qs = custom_events_qs.filter(status="PUBLISHED", start_time__lte=now + timezone.timedelta(days=365))
        if user.role == "STUDENT":
            try:
                student = StudentProfile.objects.get(user=user)
                custom_events_qs = custom_events_qs.filter(
                    Q(target__in=["ALL", "STUDENT"]) |
                    Q(target="DEPARTMENT", department=student.department) |
                    Q(target="COURSE", course__department=student.department, course__semester=student.semester)
                )
            except StudentProfile.DoesNotExist:
                custom_events_qs = custom_events_qs.filter(target="ALL")
        elif user.role == "TEACHER":
            try:
                teacher = TeacherProfile.objects.get(user=user)
                custom_events_qs = custom_events_qs.filter(
                    Q(target__in=["ALL", "TEACHER"]) |
                    Q(target="DEPARTMENT", department=teacher.department) |
                    Q(target="COURSE", course__teacher=teacher)
                )
            except TeacherProfile.DoesNotExist:
                custom_events_qs = custom_events_qs.filter(target="ALL")

    # 2. Timetable Events
    timetable_qs = Timetable.objects.select_related("course", "teacher", "department").all()
    if user.role == "STUDENT":
        try:
            student = StudentProfile.objects.get(user=user)
            timetable_qs = timetable_qs.filter(department=student.department, semester=student.semester)
        except StudentProfile.DoesNotExist:
            pass
    elif user.role == "TEACHER":
        try:
            teacher = TeacherProfile.objects.get(user=user)
            timetable_qs = timetable_qs.filter(teacher=teacher)
        except TeacherProfile.DoesNotExist:
            pass

    # 3. Assignments
    assignment_qs = Assignment.objects.select_related("course", "teacher", "teacher__user").all()
    if user.role == "STUDENT":
        try:
            student = StudentProfile.objects.get(user=user)
            assignment_qs = assignment_qs.filter(course__department=student.department, course__semester=student.semester)
        except StudentProfile.DoesNotExist:
            pass
    elif user.role == "TEACHER":
        try:
            teacher = TeacherProfile.objects.get(user=user)
            assignment_qs = assignment_qs.filter(teacher=teacher)
        except TeacherProfile.DoesNotExist:
            pass

    # 4. Announcements
    announcement_qs = Announcement.objects.select_related("created_by", "department", "course").filter(
        status="PUBLISHED", publish_at__lte=now
    )

    category_filter = clean_query_param(request.GET.get("category"))
    calendar_events = []

    # Custom Admin Events
    for evt in custom_events_qs:
        if not category_filter or category_filter == evt.category:
            badge_class = "bg-danger" if evt.category == "EXAM" else ("bg-success" if evt.category == "HOLIDAY" else ("bg-warning text-dark" if evt.category == "ASSIGNMENT" else "bg-primary"))
            calendar_events.append({
                "id": evt.id,
                "is_custom": True,
                "title": evt.title,
                "code": evt.get_category_display(),
                "category": evt.category,
                "badge_class": badge_class,
                "day_or_date": evt.start_time.strftime("%d %b %Y (%a)"),
                "time_slot": evt.start_time.strftime("%I:%M %p") if evt.start_time else "All Day",
                "detail": evt.location or (evt.department.name if evt.department else "Campus Wide"),
                "instructor": evt.created_by.get_full_name() if evt.created_by else "Academic Admin",
                "status": evt.status,
            })

    # Timetable Lectures
    if not category_filter or category_filter == "LECTURE":
        for slot in timetable_qs:
            calendar_events.append({
                "is_custom": False,
                "title": f"Lecture: {slot.course.name}",
                "code": slot.course.code,
                "category": "LECTURE",
                "badge_class": "bg-primary",
                "day_or_date": slot.day,
                "time_slot": f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}",
                "detail": f"Classroom {slot.classroom}",
                "instructor": slot.teacher.full_name if slot.teacher else "Faculty Member",
                "status": "PUBLISHED",
            })

    # Assignment Deadlines
    if not category_filter or category_filter == "ASSIGNMENT":
        for assign in assignment_qs:
            calendar_events.append({
                "is_custom": False,
                "title": f"Deadline: {assign.title}",
                "code": assign.course.code,
                "category": "ASSIGNMENT",
                "badge_class": "bg-warning text-dark",
                "day_or_date": assign.due_date.strftime("%d %b %Y (%a)") if assign.due_date else "Upcoming",
                "time_slot": "Due Date",
                "detail": f"Max Marks: {assign.total_marks}",
                "instructor": assign.teacher.full_name if assign.teacher else "Faculty Member",
                "status": "PUBLISHED",
            })

    context = {
        "today": today,
        "calendar_events": calendar_events,
        "timetable_events": timetable_qs,
        "assignment_events": assignment_qs,
        "announcement_events": announcement_qs[:5],
        "category_filter": category_filter,
    }
    return render(request, "dashboard/calendar.html", context)


@login_required
@admin_or_teacher_required
def calendar_event_create(request):
    if request.method == "POST":
        form = AcademicEventForm(request.POST)
        if form.is_valid():
            evt = form.save(commit=False)
            evt.created_by = request.user
            evt.save()
            messages.success(request, "Academic calendar event created successfully.")
            return redirect("calendar")
    else:
        form = AcademicEventForm()

    return render(request, "dashboard/calendar_event_form.html", {"form": form})


@login_required
@admin_or_teacher_required
def calendar_event_update(request, pk):
    evt = get_object_or_404(AcademicEvent, pk=pk)
    if request.user.role == "TEACHER" and evt.created_by != request.user:
        messages.error(request, "You can only edit events created by you.")
        return redirect("calendar")

    if request.method == "POST":
        form = AcademicEventForm(request.POST, instance=evt)
        if form.is_valid():
            form.save()
            messages.success(request, "Academic event updated successfully.")
            return redirect("calendar")
    else:
        form = AcademicEventForm(instance=evt)

    return render(request, "dashboard/calendar_event_form.html", {"form": form, "event": evt})


@login_required
@admin_or_teacher_required
def calendar_event_delete(request, pk):
    evt = get_object_or_404(AcademicEvent, pk=pk)
    if request.user.role == "TEACHER" and evt.created_by != request.user:
        messages.error(request, "You can only delete events created by you.")
        return redirect("calendar")

    if request.method == "POST":
        evt.delete()
        messages.success(request, "Academic event removed from calendar.")
        return redirect("calendar")

    return render(request, "dashboard/calendar_event_delete.html", {"event": evt})


# ==========================================================
# HELPER REDIRECTS
# ==========================================================
from accounts.views import profile as accounts_profile_view


@login_required
def dashboard_profile(request):
    from accounts.views import profile as accounts_profile_view
    return accounts_profile_view(request)

def dashboard_notifications(request):
    return redirect("announcement_list")

@login_required
def recent_activity(request):
    return redirect("admin_dashboard")

@login_required
def quick_links(request):
    return redirect("admin_dashboard")

@login_required
def about(request):
    return redirect("admin_dashboard")

@login_required
def student_results(request):
    from results.views import my_results
    return my_results(request)

@login_required
def student_assignments(request):
    from assignments.views import assignment_list
    return assignment_list(request)

@login_required
def student_notes(request):
    from notes.views import note_list
    return note_list(request)

@login_required
def student_leaves(request):
    return redirect("leave_list")

@login_required
def student_announcements(request):
    from announcements.views import announcement_list
    return announcement_list(request)


# ==========================================
# CENTRAL ACADEMIC REPORTS HUB
# ==========================================
from students.models import StudentProfile
from teachers.models import TeacherProfile
from courses.models import Course
from attendance.models import AttendanceSession
from results.models import Result
from assignments.models import Assignment
from timetable.models import Timetable
from notes.models import Note


@login_required
def academic_reports(request):
    user = request.user

    context = {
        "title": "Academic Reports & Data Export Center",
        "total_students": StudentProfile.objects.count(),
        "total_teachers": TeacherProfile.objects.count(),
        "total_courses": Course.objects.filter(status="ACTIVE").count(),
        "total_attendance_sessions": AttendanceSession.objects.count(),
        "total_results": Result.objects.count(),
        "total_assignments": Assignment.objects.count(),
        "total_timetables": Timetable.objects.filter(is_active=True).count(),
        "total_notes": Note.objects.filter(status="PUBLISHED").count(),
    }
    return render(request, "dashboard/academic_reports.html", context)


# ==========================================
# ADVANCED ACADEMIC ANALYTICS DASHBOARD PAGE
# ==========================================
@login_required
def academic_analytics(request):
    user = request.user
    context = {
        "title": "Academic Performance & Analytics Dashboard",
        "role": user.role,
    }
    return render(request, "dashboard/academic_analytics.html", context)
