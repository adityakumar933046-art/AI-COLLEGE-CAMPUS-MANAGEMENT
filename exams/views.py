import datetime
from django.utils import timezone
import csv
from openpyxl import Workbook
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse

from accounts.decorators import admin_required, admin_or_teacher_required
from students.models import StudentProfile
from teachers.models import TeacherProfile
from announcements.models import Announcement
from dashboard.models import AcademicEvent

from .models import Exam, ExamSchedule
from .forms import ExamForm, ExamScheduleForm


def clean_query_param(val):
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str.lower() in ("", "none", "null", "undefined"):
        return None
    return val_str


# ==========================================
# EXAM LIST (ADMIN)
# ==========================================
@login_required
@admin_required
def exam_list(request):
    exams = Exam.objects.select_related("department", "created_by").all()

    search = clean_query_param(request.GET.get("search"))
    if search:
        exams = exams.filter(Q(name__icontains=search) | Q(department__name__icontains=search))

    status_filter = clean_query_param(request.GET.get("status"))
    if status_filter:
        exams = exams.filter(status=status_filter)

    type_filter = clean_query_param(request.GET.get("exam_type"))
    if type_filter:
        exams = exams.filter(exam_type=type_filter)

    sem_filter = clean_query_param(request.GET.get("semester"))
    if sem_filter and sem_filter.isdigit():
        exams = exams.filter(semester=int(sem_filter))

    paginator = Paginator(exams, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "exams/exam_list.html",
        {
            "exams": page_obj,
            "page_obj": page_obj,
            "search": search,
            "status_filter": status_filter,
            "type_filter": type_filter,
            "title": "Academic Examination Management",
        }
    )


# ==========================================
# CREATE EXAM
# ==========================================
@login_required
@admin_required
def exam_create(request):
    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, f"Examination '{exam.name}' created successfully.")
            return redirect("exam_detail", pk=exam.pk)
        else:
            messages.error(request, "Please correct the errors in the exam form.")
    else:
        form = ExamForm()

    return render(request, "exams/exam_form.html", {"form": form, "title": "Create Academic Examination"})


# ==========================================
# EXAM DETAIL
# ==========================================
@login_required
def exam_detail(request, pk):
    exam = get_object_or_404(Exam.objects.select_related("department"), pk=pk)
    schedules = exam.schedules.select_related("course", "invigilator", "invigilator__user").all()

    return render(
        request,
        "exams/exam_detail.html",
        {
            "exam": exam,
            "schedules": schedules,
            "is_admin": request.user.role == "ADMIN",
            "title": f"Exam Details - {exam.name}",
        }
    )


# ==========================================
# UPDATE EXAM
# ==========================================
@login_required
@admin_required
def exam_update(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f"Examination '{exam.name}' updated successfully.")
            return redirect("exam_detail", pk=exam.pk)
    else:
        form = ExamForm(instance=exam)

    return render(request, "exams/exam_form.html", {"form": form, "exam": exam, "title": "Edit Examination"})


# ==========================================
# DELETE EXAM
# ==========================================
@login_required
@admin_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == "POST":
        name = exam.name
        exam.delete()
        messages.success(request, f"Examination '{name}' deleted successfully.")
        return redirect("exam_list")

    return render(request, "exams/exam_confirm_delete.html", {"exam": exam, "title": "Confirm Delete Examination"})


# ==========================================
# PUBLISH EXAM
# ==========================================
@login_required
@admin_required
def exam_publish(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    exam.status = "PUBLISHED"
    exam.save()

    # Create announcement for department students
    Announcement.objects.create(
        title=f"Examination Published: {exam.name}",
        message=f"{exam.get_exam_type_display()} for Department {exam.department.name} (Semester {exam.semester}) has been published.",
        category="EXAM",
        priority="URGENT",
        target="STUDENT",
        department=exam.department,
        created_by=request.user,
        status="PUBLISHED"
    )

    # Sync into Academic Calendar Event
    AcademicEvent.objects.get_or_create(
        title=f"EXAM: {exam.name}",
        defaults={
            "description": f"Official {exam.get_exam_type_display()}",
            "category": "EXAM",
            "priority": "URGENT",
            "target": "STUDENT",
            "department": exam.department,
            "semester": exam.semester,
            "start_time": datetime.datetime.combine(exam.start_date, datetime.time.min),
            "end_time": datetime.datetime.combine(exam.end_date, datetime.time.max),
            "status": "UPCOMING",
            "created_by": request.user
        }
    )

    messages.success(request, f"Examination '{exam.name}' published successfully.")
    return redirect("exam_detail", pk=exam.pk)


# ==========================================
# CANCEL EXAM
# ==========================================
@login_required
@admin_required
def exam_cancel(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    exam.status = "CANCELLED"
    exam.save()

    Announcement.objects.create(
        title=f"Examination Cancelled: {exam.name}",
        message=f"{exam.name} scheduled for Semester {exam.semester} has been CANCELLED.",
        category="EXAM",
        priority="URGENT",
        target="STUDENT",
        department=exam.department,
        created_by=request.user,
        status="PUBLISHED"
    )

    messages.success(request, f"Examination '{exam.name}' cancelled.")
    return redirect("exam_detail", pk=exam.pk)


# ==========================================
# CREATE EXAM SCHEDULE
# ==========================================
@login_required
@admin_required
def schedule_create(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.method == "POST":
        form = ExamScheduleForm(request.POST, exam=exam)
        if form.is_valid():
            sched = form.save(commit=False)
            sched.exam = exam
            sched.save()
            messages.success(request, f"Schedule for '{sched.course.code}' added successfully.")
            return redirect("exam_detail", pk=exam.pk)
        else:
            messages.error(request, "Please correct the errors in the schedule form below.")
    else:
        form = ExamScheduleForm(exam=exam)

    return render(request, "exams/schedule_form.html", {"form": form, "exam": exam, "title": "Add Exam Schedule Slot"})


# ==========================================
# UPDATE EXAM SCHEDULE
# ==========================================
@login_required
@admin_required
def schedule_update(request, pk):
    sched = get_object_or_404(ExamSchedule.objects.select_related("exam"), pk=pk)
    exam = sched.exam
    if request.method == "POST":
        form = ExamScheduleForm(request.POST, instance=sched, exam=exam)
        if form.is_valid():
            form.save()
            # Notify affected students of timing update
            if exam.status == "PUBLISHED":
                Announcement.objects.create(
                    title=f"Exam Schedule Updated: {sched.course.code}",
                    message=f"The exam schedule for {sched.course.name} ({exam.name}) has been updated to {sched.date} ({sched.start_time} - {sched.end_time}) in Room {sched.room}.",
                    category="EXAM",
                    priority="IMPORTANT",
                    target="STUDENT",
                    department=exam.department,
                    created_by=request.user,
                    status="PUBLISHED"
                )
            messages.success(request, f"Exam schedule for '{sched.course.code}' updated successfully.")
            return redirect("exam_detail", pk=exam.pk)
    else:
        form = ExamScheduleForm(instance=sched, exam=exam)

    return render(request, "exams/schedule_form.html", {"form": form, "exam": exam, "sched": sched, "title": "Edit Exam Schedule Slot"})


# ==========================================
# DELETE EXAM SCHEDULE
# ==========================================
@login_required
@admin_required
def schedule_delete(request, pk):
    sched = get_object_or_404(ExamSchedule, pk=pk)
    exam_id = sched.exam_id
    sched.delete()
    messages.success(request, "Exam schedule slot deleted.")
    return redirect("exam_detail", pk=exam_id)


# ==========================================
# MY EXAMS (STUDENT)
# ==========================================
@login_required
def my_exams(request):
    try:
        student = StudentProfile.objects.filter(user=request.user).first()
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard_redirect")

    schedules = ExamSchedule.objects.filter(
        exam__status="PUBLISHED",
        exam__department=student.department,
        exam__semester=student.semester,
        section__iexact=student.section
    ).select_related("exam", "course", "invigilator", "invigilator__user").order_by("date", "start_time")

    return render(
        request,
        "exams/my_exams.html",
        {
            "schedules": schedules,
            "student": student,
            "title": "My Examination Schedule",
        }
    )


# ==========================================
# MY EXAM DUTIES (TEACHER)
# ==========================================
@login_required
@admin_or_teacher_required
def my_exam_duties(request):
    try:
        teacher = TeacherProfile.objects.filter(user=request.user).first()
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard_redirect")

    duties = ExamSchedule.objects.filter(
        invigilator=teacher
    ).select_related("exam", "course").order_by("date", "start_time")

    return render(
        request,
        "exams/my_duties.html",
        {
            "duties": duties,
            "teacher": teacher,
            "title": "My Invigilation Duties",
        }
    )


# ==========================================
# EXPORT EXAM SCHEDULE EXCEL & CSV
# ==========================================
@login_required
def export_exam_schedule_excel(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    schedules = exam.schedules.select_related("course", "invigilator", "invigilator__user").all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Exam Schedule"

    ws.append(["Course Code", "Course Name", "Date", "Start Time", "End Time", "Room", "Section", "Invigilator", "Instructions"])

    for s in schedules.order_by("date", "start_time"):
        ws.append([
            s.course.code if s.course else "N/A",
            s.course.name if s.course else "N/A",
            s.date.strftime("%Y-%m-%d") if s.date else "N/A",
            s.start_time.strftime("%H:%M") if s.start_time else "N/A",
            s.end_time.strftime("%H:%M") if s.end_time else "N/A",
            s.room,
            s.section,
            s.invigilator.full_name if s.invigilator else "Unassigned",
            s.instructions,
        ])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="exam_schedule_{exam.id}.xlsx"'
    wb.save(response)
    return response


@login_required
def export_exam_schedule_csv(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    schedules = exam.schedules.select_related("course", "invigilator", "invigilator__user").all()

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="exam_schedule_{exam.id}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Course Code", "Course Name", "Date", "Start Time", "End Time", "Room", "Section", "Invigilator", "Instructions"])

    for s in schedules.order_by("date", "start_time"):
        writer.writerow([
            s.course.code if s.course else "N/A",
            s.course.name if s.course else "N/A",
            s.date.strftime("%Y-%m-%d") if s.date else "N/A",
            s.start_time.strftime("%H:%M") if s.start_time else "N/A",
            s.end_time.strftime("%H:%M") if s.end_time else "N/A",
            s.room,
            s.section,
            s.invigilator.full_name if s.invigilator else "Unassigned",
            s.instructions,
        ])

    return response
