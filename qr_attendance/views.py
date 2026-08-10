from attendance.models import AttendanceSession, Attendance
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from accounts.decorators import admin_required, admin_or_teacher_required

from .models import QRSession
from .forms import QRSessionForm


# ==========================================
# QR SESSION LIST
# ==========================================

@login_required
@admin_or_teacher_required
def qr_session_list(request):

    sessions = QRSession.objects.select_related(
        "course",
        "teacher",
        "teacher__user"
    ).all()

    search = request.GET.get("search")

    if search:

        sessions = sessions.filter(

            Q(course__code__icontains=search) |
            Q(course__name__icontains=search) |
            Q(teacher__user__first_name__icontains=search) |
            Q(teacher__user__last_name__icontains=search)

        )

    paginator = Paginator(
        sessions,
        10
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        "sessions": page_obj,

        "page_obj": page_obj,

        "search": search,

    }

    return render(
        request,
        "qr_attendance/session_list.html",
        context
    )


# ==========================================
# CREATE QR SESSION
# ==========================================

@login_required
@admin_or_teacher_required
def create_qr_session(request):

    if request.method == "POST":

        form = QRSessionForm(request.POST)

        if form.is_valid():

            session = form.save()

            messages.success(
                request,
                "QR Session Created Successfully."
            )

            return redirect(
                "qr_session_detail",
                pk=session.pk
            )

    else:

        form = QRSessionForm()

    return render(
        request,
        "qr_attendance/create_session.html",
        {
            "form": form
        }
    )


# ==========================================
# QR SESSION DETAIL
# ==========================================

@login_required
@admin_or_teacher_required
def qr_session_detail(request, pk):

    session = get_object_or_404(
        QRSession.objects.select_related(
            "course",
            "teacher",
            "teacher__user"
        ),
        pk=pk
    )

    context = {

        "session": session,

    }

    return render(
        request,
        "qr_attendance/session_detail.html",
        context
    )


# ==========================================
# CLOSE SESSION
# ==========================================

@login_required
@admin_or_teacher_required
def close_session(request, pk):

    session = get_object_or_404(
        QRSession,
        pk=pk
    )

    session.status = "CLOSED"

    session.save()

    messages.success(
        request,
        "QR Session Closed."
    )

    return redirect(
        "qr_session_detail",
        pk=pk
    )

import uuid
from datetime import timedelta

from django.http import JsonResponse
from django.utils import timezone

from .models import QRSession, QRAttendance
from students.models import StudentProfile


# ==========================================
# REFRESH QR (AUTO EVERY 10 SEC)
# ==========================================

@login_required
@admin_or_teacher_required
def refresh_qr(request, pk):

    session = get_object_or_404(
        QRSession,
        pk=pk
    )

    session.token = uuid.uuid4()

    session.created_at = timezone.now()

    session.expires_at = timezone.now() + timedelta(seconds=10)

    session.status = "ACTIVE"

    session.save()

    return JsonResponse({

        "token": str(session.token),

        "expires_at": session.expires_at.strftime("%H:%M:%S"),

    })


# ==========================================
# STUDENT SCAN QR
# ==========================================

@login_required
@login_required
def scan_qr(request, token):
    session = get_object_or_404(QRSession, token=token, status="ACTIVE")

    if session.is_expired:
        return render(request, "qr_attendance/attendance_failed.html", {"message": "QR Code Expired. Please scan the latest QR code."})

    try:
        student = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return render(request, "qr_attendance/attendance_failed.html", {"message": "Unauthorized. Only registered students can mark attendance."})

    if QRAttendance.objects.filter(session=session, student=student).exists():
        return render(request, "qr_attendance/attendance_failed.html", {"message": "Attendance already recorded for this session."})

    # Create QR attendance record
    qr_rec = QRAttendance.objects.create(session=session, student=student)

    # Sync with main Attendance module if matching session exists or create one
    try:
        att_session, _ = AttendanceSession.objects.get_or_create(
            course=session.course,
            attendance_date=timezone.now().date(),
            section="A",
            defaults={
                "department": session.course.department,
                "teacher": session.teacher,
                "semester": session.course.semester,
                "lecture_no": 1,
                "status": "OPEN",
            }
        )
        Attendance.objects.get_or_create(
            session=att_session,
            student=student,
            defaults={"status": "PRESENT", "marked_by": request.user}
        )
    except Exception as e:
        pass

    return render(request, "qr_attendance/attendance_success.html", {"session": session})

# ==========================================
# LIVE ATTENDANCE COUNT API
# ==========================================

@login_required
@admin_or_teacher_required
def attendance_count(request, pk):

    session = get_object_or_404(
        QRSession,
        pk=pk
    )

    count = session.attendance_records.count()

    return JsonResponse({

        "count": count

    })


# ==========================================
# DELETE SESSION
# ==========================================

@login_required
@admin_or_teacher_required
def delete_session(request, pk):

    session = get_object_or_404(
        QRSession,
        pk=pk
    )

    if request.method == "POST":

        session.delete()

        messages.success(
            request,
            "QR Session deleted successfully."
        )

        return redirect(
            "qr_session_list"
        )

    return render(
        request,
        "qr_attendance/delete_session.html",
        {
            "session": session
        }
    )