from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q

from students.models import StudentProfile
from teachers.models import TeacherProfile
from leaves.models import Leave
from results.models import Result
from announcements.models import Announcement
from courses.models import Course
from accounts.models import User

# Allowed fields for update
STUDENT_ALLOWED_FIELDS = ["phone", "email", "city", "state", "status", "section", "semester"]

@transaction.atomic
def update_student_action(user, student_id, changes):
    if user.role not in ["ADMIN", "TEACHER"]:
        return {"success": False, "message": "Permission denied: Only Admin or Faculty can update student records."}

    student = StudentProfile.objects.filter(id=student_id).select_related('user').first()
    if not student:
        return {"success": False, "message": "Student record not found."}

    if user.role == "TEACHER":
        tp = getattr(user, 'teacher_profile', None)
        if not tp or student.department != tp.department:
            return {"success": False, "message": "Permission denied: You can only update students in your assigned department."}

    updated_fields = []
    if "phone" in changes:
        student.phone = str(changes["phone"]).strip()
        updated_fields.append(f"Phone -> {student.phone}")

    if "city" in changes:
        student.city = str(changes["city"]).strip()
        updated_fields.append(f"City -> {student.city}")

    if "email" in changes:
        email = str(changes["email"]).strip().lower()
        if User.objects.filter(email=email).exclude(pk=student.user.pk).exists():
            return {"success": False, "message": f"Email '{email}' is already in use by another account."}
        student.user.email = email
        student.user.save()
        updated_fields.append(f"Email -> {email}")

    student.save()
    return {
        "success": True,
        "message": f"Successfully updated student {student.user.get_full_name()} ({student.roll_no}): {', '.join(updated_fields)}"
    }

@transaction.atomic
def approve_leave_action(user, leave_id, remarks="Approved via Campus AI"):
    if user.role not in ["ADMIN", "TEACHER"]:
        return {"success": False, "message": "Permission denied: Only Admin or Faculty can approve leave applications."}

    leave = Leave.objects.filter(id=leave_id).select_related('applicant').first()
    if not leave:
        return {"success": False, "message": "Leave application not found."}

    if user.role == "TEACHER":
        tp = getattr(user, 'teacher_profile', None)
        st_prof = getattr(leave.applicant, 'student_profile', None)
        if not tp or not st_prof or st_prof.department != tp.department:
            return {"success": False, "message": "Permission denied: You are not authorized to approve leave for this student."}

    leave.status = "APPROVED"
    leave.reviewed_by = user
    leave.remarks = remarks
    leave.save()

    # Notify student via existing Announcement system
    Announcement.objects.create(
        title="Academic Leave Approved",
        message=f"Your {leave.get_leave_type_display()} from {leave.from_date} to {leave.to_date} has been APPROVED.",
        category="GENERAL",
        priority="IMPORTANT",
        target="STUDENT",
        created_by=user,
        status="PUBLISHED"
    )

    return {
        "success": True,
        "message": f"Successfully APPROVED leave application for {leave.applicant.get_full_name()}."
    }

@transaction.atomic
def reject_leave_action(user, leave_id, remarks="Rejected via Campus AI"):
    if user.role not in ["ADMIN", "TEACHER"]:
        return {"success": False, "message": "Permission denied: Only Admin or Faculty can reject leave applications."}

    leave = Leave.objects.filter(id=leave_id).select_related('applicant').first()
    if not leave:
        return {"success": False, "message": "Leave application not found."}

    if user.role == "TEACHER":
        tp = getattr(user, 'teacher_profile', None)
        st_prof = getattr(leave.applicant, 'student_profile', None)
        if not tp or not st_prof or st_prof.department != tp.department:
            return {"success": False, "message": "Permission denied: You are not authorized to reject leave for this student."}

    leave.status = "REJECTED"
    leave.reviewed_by = user
    leave.remarks = remarks
    leave.save()

    # Notify student via existing Announcement system
    Announcement.objects.create(
        title="Academic Leave Rejected",
        message=f"Your {leave.get_leave_type_display()} from {leave.from_date} to {leave.to_date} was REJECTED. Reason: {remarks}",
        category="GENERAL",
        priority="IMPORTANT",
        target="STUDENT",
        created_by=user,
        status="PUBLISHED"
    )

    return {
        "success": True,
        "message": f"Successfully REJECTED leave application for {leave.applicant.get_full_name()}."
    }

@transaction.atomic
def create_announcement_action(user, title, message, target="ALL", priority="GENERAL"):
    if user.role not in ["ADMIN", "TEACHER"]:
        return {"success": False, "message": "Permission denied: Only Admin or Faculty can create announcements."}

    announcement = Announcement.objects.create(
        title=title,
        message=message,
        target=target,
        priority=priority,
        created_by=user,
        status="PUBLISHED"
    )

    return {
        "success": True,
        "message": f"Successfully published campus announcement: '{announcement.title}' (Target: {announcement.target})."
    }
