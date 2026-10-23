import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, FileResponse, Http404

from accounts.decorators import admin_required, admin_or_teacher_required
from students.models import StudentProfile
from teachers.models import TeacherProfile
from courses.models import Course
from announcements.models import Announcement

from .models import Leave
from .forms import LeaveForm, LeaveStatusForm


def clean_query_param(val):
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str.lower() in ("", "none", "null", "undefined"):
        return None
    return val_str


# ==========================================
# ADMIN LEAVE LIST
# ==========================================
@login_required
@admin_required
def leave_list(request):
    leaves = Leave.objects.select_related("applicant").all()

    search = clean_query_param(request.GET.get("search"))
    if search:
        leaves = leaves.filter(
            Q(applicant__username__icontains=search) |
            Q(applicant__first_name__icontains=search) |
            Q(applicant__last_name__icontains=search) |
            Q(reason__icontains=search)
        )

    status_filter = clean_query_param(request.GET.get("status"))
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    leave_type_filter = clean_query_param(request.GET.get("leave_type"))
    if leave_type_filter:
        leaves = leaves.filter(leave_type=leave_type_filter)

    paginator = Paginator(leaves, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "leaves/leave_list.html",
        {
            "leaves": page_obj,
            "page_obj": page_obj,
            "search": search,
            "status_filter": status_filter,
            "leave_type_filter": leave_type_filter,
            "title": "Academic Leave Management",
        }
    )


# ==========================================
# TEACHER LEAVE REQUESTS
# ==========================================
@login_required
@admin_or_teacher_required
def teacher_leave_list(request):
    if request.user.role == "ADMIN":
        return redirect("leave_list")

    try:
        teacher = TeacherProfile.objects.filter(user=request.user).first()
    except TeacherProfile.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect("dashboard_redirect")

    # Filter leaves of students in courses taught by this teacher or same department
    assigned_courses = Course.objects.filter(teacher=teacher)
    dept_students = StudentProfile.objects.filter(department=teacher.department).values_list("user_id", flat=True)

    leaves = Leave.objects.filter(
        Q(applicant_id__in=dept_students) |
        Q(applicant__student_profile__department=teacher.department)
    ).select_related("applicant").distinct().order_by("-applied_at")

    status_filter = clean_query_param(request.GET.get("status"))
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    paginator = Paginator(leaves, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "leaves/teacher_leave_list.html",
        {
            "leaves": page_obj,
            "page_obj": page_obj,
            "status_filter": status_filter,
            "title": "Student Leave Requests",
        }
    )


# ==========================================
# MY LEAVES (STUDENT)
# ==========================================
@login_required
def my_leaves(request):
    leaves = Leave.objects.filter(applicant=request.user).order_by("-applied_at")

    status_filter = clean_query_param(request.GET.get("status"))
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    return render(
        request,
        "leaves/my_leaves.html",
        {
            "leaves": leaves,
            "status_filter": status_filter,
            "title": "My Leave Applications",
        }
    )


# ==========================================
# APPLY LEAVE
# ==========================================
@login_required
def apply_leave(request):
    if request.method == "POST":
        form = LeaveForm(request.POST, request.FILES)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.applicant = request.user

            # Check overlap for same student
            overlap = Leave.objects.filter(
                applicant=request.user,
                status__in=["PENDING", "APPROVED"],
                from_date__lte=leave.to_date,
                to_date__gte=leave.from_date
            ).exists()

            if overlap:
                messages.error(request, "An overlapping leave application already exists for the selected dates.")
                return render(request, "leaves/apply_leave.html", {"form": form, "title": "Apply for Leave"})

            leave.save()

            # Create notification for teachers/admin
            Announcement.objects.create(
                title=f"New Leave Application: {request.user.get_full_name()}",
                message=f"Student {request.user.get_full_name()} submitted a {leave.get_leave_type_display()} from {leave.from_date} to {leave.to_date}.",
                category="GENERAL",
                priority="IMPORTANT",
                target="TEACHER",
                created_by=request.user,
                status="PUBLISHED"
            )

            messages.success(request, "Leave application submitted successfully.")
            return redirect("my_leaves")
        else:
            messages.error(request, "Please correct the errors in the leave form below.")
    else:
        form = LeaveForm()

    return render(request, "leaves/apply_leave.html", {"form": form, "title": "Apply for Leave"})


# ==========================================
# LEAVE DETAIL
# ==========================================
@login_required
def leave_detail(request, pk):
    leave = get_object_or_404(Leave.objects.select_related("applicant", "reviewed_by"), pk=pk)

    # Permission check
    is_owner = (leave.applicant == request.user)
    is_admin = (request.user.role == "ADMIN")
    is_teacher = False
    if request.user.role == "TEACHER" and hasattr(request.user, "teacher_profile"):
        st_prof = getattr(leave.applicant, "student_profile", None)
        if st_prof and st_prof.department == request.user.teacher_profile.department:
            is_teacher = True

    if not (is_owner or is_admin or is_teacher):
        messages.error(request, "You are not authorized to view this leave application.")
        return redirect("my_leaves")

    return render(
        request,
        "leaves/leave_detail.html",
        {
            "leave": leave,
            "is_owner": is_owner,
            "can_review": (is_admin or is_teacher),
            "title": "Leave Application Details",
        }
    )


# ==========================================
# APPROVE LEAVE
# ==========================================
@login_required
@admin_or_teacher_required
def approve_leave(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    
    remarks = request.POST.get("remarks", "").strip() or "Leave application approved."
    leave.status = "APPROVED"
    leave.reviewed_by = request.user
    leave.remarks = remarks
    leave.save()

    # Notify student
    Announcement.objects.create(
        title="Academic Leave Approved",
        message=f"Your {leave.get_leave_type_display()} from {leave.from_date} to {leave.to_date} has been APPROVED.",
        category="GENERAL",
        priority="IMPORTANT",
        target="STUDENT",
        created_by=request.user,
        status="PUBLISHED"
    )

    messages.success(request, f"Leave application for {leave.applicant.get_full_name()} approved.")
    fallback = "leave_list" if request.user.role == "ADMIN" else "teacher_leave_list"
    return redirect(request.META.get("HTTP_REFERER", fallback))


# ==========================================
# REJECT LEAVE
# ==========================================
@login_required
@admin_or_teacher_required
def reject_leave(request, pk):
    leave = get_object_or_404(Leave, pk=pk)

    if request.method == "POST":
        remarks = request.POST.get("remarks", "").strip()
        if not remarks:
            messages.error(request, "Rejection reason is required.")
            return redirect("leave_detail", pk=pk)

        leave.status = "REJECTED"
        leave.reviewed_by = request.user
        leave.remarks = remarks
        leave.save()

        # Notify student
        Announcement.objects.create(
            title="Academic Leave Rejected",
            message=f"Your {leave.get_leave_type_display()} from {leave.from_date} to {leave.to_date} was REJECTED. Reason: {remarks}",
            category="GENERAL",
            priority="IMPORTANT",
            target="STUDENT",
            created_by=request.user,
            status="PUBLISHED"
        )

        messages.success(request, f"Leave application for {leave.applicant.get_full_name()} rejected.")
        fallback = "leave_list" if request.user.role == "ADMIN" else "teacher_leave_list"
    return redirect(request.META.get("HTTP_REFERER", fallback))

    return redirect("leave_detail", pk=pk)


# ==========================================
# CANCEL LEAVE (STUDENT)
# ==========================================
@login_required
def cancel_leave(request, pk):
    leave = get_object_or_404(Leave, pk=pk, applicant=request.user)
    if leave.status != "PENDING":
        messages.error(request, "Only pending leave applications can be cancelled.")
        return redirect("my_leaves")

    leave.status = "CANCELLED"
    leave.save()
    messages.success(request, "Leave application cancelled.")
    return redirect("my_leaves")


# ==========================================
# DOWNLOAD MEDICAL CERTIFICATE
# ==========================================
@login_required
def download_certificate(request, pk):
    leave = get_object_or_404(Leave, pk=pk)

    # Permission check
    is_owner = (leave.applicant == request.user)
    is_admin = (request.user.role == "ADMIN")
    is_teacher = False
    if request.user.role == "TEACHER" and hasattr(request.user, "teacher_profile"):
        st_prof = getattr(leave.applicant, "student_profile", None)
        if st_prof and st_prof.department == request.user.teacher_profile.department:
            is_teacher = True

    if not (is_owner or is_admin or is_teacher):
        messages.error(request, "You are not authorized to access this document.")
        return redirect("my_leaves")

    if not leave.medical_certificate or not os.path.exists(leave.medical_certificate.path):
        raise Http404("Medical certificate file not found.")

    return FileResponse(open(leave.medical_certificate.path, 'rb'), filename=os.path.basename(leave.medical_certificate.name))
