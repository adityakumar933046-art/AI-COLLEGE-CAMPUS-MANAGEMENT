from accounts.decorators import admin_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from attendance.models import AttendanceSession, Attendance
from .models import TeacherProfile
from leaves.forms import LeaveForm
from .forms import (
    TeacherCreateForm,
    TeacherUpdateForm,
    TeacherProfileForm,
    TeacherExcelImportForm,
)

from .services import (
    create_teacher,
    bulk_import_teachers,
    export_teachers_excel as export_teachers_excel_service,
    export_teachers_csv as export_teachers_csv_service,
    export_credentials,
    export_error_report,
)

from courses.models import Course
from students.models import StudentProfile
from attendance.models import Attendance
from assignments.models import Assignment
from notes.models import Note
from results.models import Result
from timetable.models import Timetable
from announcements.models import Announcement
from leaves.models import Leave

import io
import pandas as pd

from django.http import HttpResponse


# ==========================================================
# TEACHER DASHBOARD
# ==========================================================

@login_required
def teacher_dashboard(request):

    teacher = get_object_or_404(
        TeacherProfile,
        user=request.user
    )

    context = {

        "teacher": teacher,

        "total_courses": Course.objects.filter(
            teacher=teacher
        ).count(),

        "total_students": StudentProfile.objects.filter(
            department=teacher.department
        ).count(),

        "total_assignments": Assignment.objects.filter(
            teacher=teacher
        ).count(),

        "total_notes": Note.objects.filter(
            teacher=teacher
        ).count(),

        "total_results": Result.objects.filter(
            teacher=teacher
        ).count(),

        "total_announcements": Announcement.objects.filter(
            target__in=["ALL", "TEACHER"]
        ).count(),

        "title": "Teacher Dashboard",

    }

    return render(
        request,
        "teachers/teacher_dashboard.html",
        context,
    )


# ==========================================================
# TEACHER PROFILE
# ==========================================================

@login_required
def teacher_profile(request):
    return redirect("profile")


@login_required
def teacher_list(request):

    teachers = TeacherProfile.objects.select_related(
        "user",
        "department",
    ).all()

    search = request.GET.get(
        "search",
        "",
    )

    if search:

        teachers = teachers.filter(

            Q(user__first_name__icontains=search) |

            Q(user__last_name__icontains=search) |

            Q(user__username__icontains=search) |

            Q(user__email__icontains=search) |

            Q(employee_id__icontains=search) |

            Q(phone__icontains=search) |

            Q(designation__icontains=search)

        )

    department = request.GET.get(
        "department"
    )

    if department:

        teachers = teachers.filter(
            department_id=department
        )

    status = request.GET.get(
        "status"
    )

    if status:

        teachers = teachers.filter(
            status=status
        )

    paginator = Paginator(
        teachers,
        10,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "teachers/teacher_list.html",
        {
            "teachers": page_obj,
            "search": search,
            "department": department,
            "status": status,
            "total_teachers": teachers.count(),
            "title": "Teacher List",
        },
    )


# ==========================================================
# TEACHER DETAIL
# ==========================================================

@login_required
def teacher_detail(request, pk):

    teacher = get_object_or_404(
        TeacherProfile.objects.select_related(
            "user",
            "department",
        ),
        pk=pk,
    )

    return render(
        request,
        "teachers/teacher_detail.html",
        {
            "teacher": teacher,
            "title": "Teacher Details",
        },
    )
# ==========================================================
# ADD TEACHER
# ==========================================================

@login_required
def add_teacher(request):

    if request.method == "POST":

        form = TeacherCreateForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            data = form.cleaned_data.copy()

            full_name = request.POST.get(
                "full_name",
                ""
            ).strip()

            parts = full_name.split(maxsplit=1)

            data["first_name"] = (
                parts[0] if len(parts) > 0 else ""
            )

            data["last_name"] = (
                parts[1] if len(parts) > 1 else ""
            )

            data["email"] = request.POST.get(
                "email",
                ""
            ).strip().lower()

            data["password"] = request.POST.get(
                "password",
                ""
            )

            try:

                result = create_teacher(
                    data=data,
                    created_by=request.user,
                )

                from accounts.services import send_teacher_credentials_email
                user_obj = result.get("user") or getattr(result.get("teacher"), "user", None)
                temp_pwd = result["password"]

                email_sent, email_err = send_teacher_credentials_email(user_obj, temp_pwd, request=request)

                if email_sent:
                    messages.success(
                        request,
                        f"Teacher created successfully. Login credentials have been sent to {user_obj.email}."
                    )
                else:
                    messages.warning(
                        request,
                        f"Teacher created successfully, but the credentials email could not be sent to {user_obj.email}. (Error: {email_err})"
                    )

                return redirect(
                    "teacher_list"
                )

            except Exception as e:

                messages.error(
                    request,
                    str(e)
                )

    else:

        form = TeacherCreateForm()

    return render(
        request,
        "teachers/teacher_add.html",
        {
            "form": form,
            "title": "Add Teacher",
        },
    )


# ==========================================================
# UPDATE TEACHER
# ==========================================================

@login_required
def update_teacher(request, pk):

    teacher = get_object_or_404(
        TeacherProfile,
        pk=pk,
    )

    if request.method == "POST":

        form = TeacherUpdateForm(
            request.POST,
            request.FILES,
            instance=teacher,
        )

        if form.is_valid():

            obj = form.save(
                commit=False
            )

            obj.updated_by = request.user

            obj.save()

            messages.success(
                request,
                "Teacher updated successfully."
            )

            return redirect(
                "teacher_detail",
                pk=teacher.pk,
            )

    else:

        form = TeacherUpdateForm(
            instance=teacher,
        )

    return render(
        request,
        "teachers/teacher_edit.html",
        {
            "teacher": teacher,
            "form": form,
            "title": "Update Teacher",
        },
    )


# ==========================================================
# DELETE TEACHER
# ==========================================================

@login_required
def delete_teacher(request, pk):

    teacher = get_object_or_404(
        TeacherProfile.objects.select_related(
            "user",
        ),
        pk=pk,
    )

    if request.method == "POST":

        user = teacher.user

        teacher.delete()

        if user:

            user.delete()

        messages.success(
            request,
            "Teacher deleted successfully."
        )

        return redirect(
            "teacher_list"
        )

    return render(
        request,
        "teachers/teacher_delete.html",
        {
            "teacher": teacher,
            "title": "Delete Teacher",
        },
    )
# ==========================================================
# TEACHER COURSES
# ==========================================================

@login_required
@login_required
def teacher_courses(request):
    teacher = get_object_or_404(
        TeacherProfile,
        user=request.user,
    )

    courses = Course.objects.filter(
        teacher=teacher
    ).select_related("department").order_by("name")

    search = request.GET.get("search", "")
    if search:
        courses = courses.filter(
            Q(name__icontains=search) | Q(code__icontains=search)
        )

    # Enrich courses for teacher
    enriched_courses = []
    for c in courses:
        enrolled_students = StudentProfile.objects.filter(department=c.department, semester=c.semester).count()
        att_sessions = AttendanceSession.objects.filter(course=c, teacher=teacher).count()
        ass_count = Assignment.objects.filter(course=c, teacher=teacher).count()
        notes_count = Note.objects.filter(course=c, teacher=teacher).count()

        enriched_courses.append({
            "course": c,
            "enrolled_students": enrolled_students,
            "att_sessions": att_sessions,
            "assignments_count": ass_count,
            "notes_count": notes_count,
        })

    paginator = Paginator(enriched_courses, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "teachers/teacher_courses.html",
        {
            "teacher": teacher,
            "courses_page": page_obj,
            "total_courses": len(enriched_courses),
            "search": search,
            "title": "My Assigned Courses",
        },
    )

# ==========================================================
# TEACHER STUDENTS
# ==========================================================

@login_required
def teacher_students(request):

    teacher = get_object_or_404(
        TeacherProfile,
        user=request.user,
    )

    students = StudentProfile.objects.filter(
        department=teacher.department
    ).select_related(
        "user"
    )

    search = request.GET.get("search", "")

    if search:

        students = students.filter(

            Q(user__first_name__icontains=search) |

            Q(user__last_name__icontains=search) |

            Q(roll_no__icontains=search) |

            Q(admission_no__icontains=search)

        )

    paginator = Paginator(
        students,
        10,
    )

    students = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "teachers/teacher_students.html",
        {
            "teacher": teacher,
            "students": students,
            "search": search,
            "total_students": students.paginator.count,
            "title": "Students",
        },
    )


# ==========================================================
# TEACHER ATTENDANCE
# ==========================================================

@login_required
def teacher_attendance(request):

    teacher = get_object_or_404(
        TeacherProfile,
        user=request.user
    )

    courses = Course.objects.filter(
        teacher=teacher
    ).select_related("department")

    semesters = (
        courses.values_list(
            "semester",
            flat=True
        ).distinct().order_by("semester")
    )

    selected_course = request.GET.get("course")
    selected_semester = request.GET.get("semester")
    attendance_date = request.GET.get("date")

    students = StudentProfile.objects.none()

    if selected_course:

        course = get_object_or_404(
            Course,
            id=selected_course,
            teacher=teacher
        )

        students = StudentProfile.objects.filter(
            department=course.department,
            semester=course.semester
        ).select_related(
            "user",
            "department"
        )

        if selected_semester:
            students = students.filter(
                semester=selected_semester
            )

    if request.method == "POST":

        course_id = request.POST.get("course")
        attendance_date = request.POST.get("date")

        if not course_id:
            messages.error(
                request,
                "Please select course."
            )
            return redirect("teacher_attendance")

        if not attendance_date:
            messages.error(
                request,
                "Please select attendance date."
            )
            return redirect(
                f"/teachers/attendance/?course={course_id}"
            )

        course = get_object_or_404(
            Course,
            id=course_id,
            teacher=teacher
        )

        session, created = AttendanceSession.objects.get_or_create(
            course=course,
            teacher=teacher,
            attendance_date=attendance_date,
            lecture_no=1,
            section="A",
            defaults={
                "department": course.department,
                "semester": course.semester,
                "status": "OPEN",
                "created_by": request.user,
            }
        )

        students = StudentProfile.objects.filter(
            department=course.department,
            semester=course.semester
        )


        for student in students:

            status = request.POST.get(
                f"attendance_{student.id}",
                "PRESENT"
            )

            remarks = request.POST.get(
                f"remarks_{student.id}",
                ""
            )

            Attendance.objects.update_or_create(
                session=session,
                student=student,
                defaults={
                    "status": status,
                    "remarks": remarks,
                    "marked_by": request.user,
                }
            )

        session.status = "CLOSED"
        session.save()

        messages.success(
            request,
            "Attendance saved successfully."
        )

        return redirect(
            f"/teachers/attendance/?course={course.id}&semester={course.semester}&date={attendance_date}"
        )

    return render(
        request,
        "teachers/teacher_attendance.html",
        {
            "teacher": teacher,
            "courses": courses,
            "semesters": semesters,
            "students": students,
            "selected_course": selected_course,
            "selected_semester": selected_semester,
            "attendance_date": attendance_date,
            "title": "Teacher Attendance",
        },
    )
# ==========================================================
# TEACHER ASSIGNMENTS
# ==========================================================

@login_required
def teacher_assignments(request):

    teacher = get_object_or_404(
        TeacherProfile,
        user=request.user,
    )

    assignments = Assignment.objects.filter(
        teacher=teacher
    ).select_related(
        "course"
    )

    search = request.GET.get("search", "")
    course = request.GET.get("course", "")

    if search:

        assignments = assignments.filter(

            Q(title__icontains=search) |

            Q(course__name__icontains=search)

        )

    if course:

        assignments = assignments.filter(
            course_id=course
        )

    paginator = Paginator(
        assignments,
        10,
    )

    assignments = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "teachers/teacher_assignments.html",
        {
            "teacher": teacher,
            "assignments": assignments,
            "courses": Course.objects.filter(
                teacher=teacher
            ),
            "search": search,
            "course": course,
            "total_assignments": assignments.paginator.count,
            "title": "Assignments",
        },
    )


# ==========================================================
# TEACHER NOTES
# ==========================================================

@login_required
def teacher_notes(request):

    teacher = get_object_or_404(
        TeacherProfile,
        user=request.user,
    )

    notes = Note.objects.filter(
        teacher=teacher
    ).select_related(
        "course"
    )

    search = request.GET.get("search", "")
    course = request.GET.get("course", "")

    if search:

        notes = notes.filter(

            Q(title__icontains=search) |

            Q(course__name__icontains=search)

        )

    if course:

        notes = notes.filter(
            course_id=course
        )

    paginator = Paginator(
        notes,
        10,
    )

    notes = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "teachers/teacher_notes.html",
        {
            "teacher": teacher,
            "notes": notes,
            "courses": Course.objects.filter(
                teacher=teacher
            ),
            "search": search,
            "course": course,
            "total_notes": notes.paginator.count,
            "title": "Notes",
        },
    )


# ==========================================================
# TEACHER RESULTS
# ==========================================================

@login_required
def teacher_results(request):

    teacher = get_object_or_404(
        TeacherProfile,
        user=request.user,
    )

    results = Result.objects.filter(
        teacher=teacher
    ).select_related(
        "student__user",
        "course",
    )

    search = request.GET.get("search", "")
    semester = request.GET.get("semester", "")

    if search:

        results = results.filter(

            Q(student__user__first_name__icontains=search) |

            Q(student__user__last_name__icontains=search) |

            Q(student__roll_no__icontains=search) |

            Q(course__name__icontains=search)

        )

    if semester:

        results = results.filter(
            semester=semester
        )

    paginator = Paginator(
        results,
        10,
    )

    results = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "teachers/teacher_results.html",
        {
            "teacher": teacher,
            "results": results,
            "search": search,
            "semester": semester,
            "total_results": results.paginator.count,
            "title": "Results",
        },
    )


# ==========================================================
# TEACHER TIMETABLE
# ==========================================================

@login_required
def teacher_timetable(request):

    teacher = get_object_or_404(
        TeacherProfile,
        user=request.user,
    )

    timetable = Timetable.objects.filter(
        teacher=teacher
    ).select_related(
        "course",
        "department",
    )

    day = request.GET.get("day", "")

    if day:

        timetable = timetable.filter(
            day=day
        )

    return render(
        request,
        "teachers/teacher_timetable.html",
        {
            "teacher": teacher,
            "timetable": timetable,
            "day": day,
            "total_classes": timetable.count(),
            "title": "My Timetable",
        },
    )
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


# ==========================================================
# TEACHER LEAVE APPLY
# ==========================================================

@login_required
def teacher_leave_apply(request):

    if request.method == "POST":

        form = LeaveForm(
            request.POST
        )

        if form.is_valid():

            leave = form.save(commit=False)

            leave.applicant = request.user

            leave.save()

            messages.success(
                request,
                "Leave application submitted successfully."
            )

            return redirect(
                "teacher_leave_requests"
            )

    else:

        form = LeaveForm()

    return render(
        request,
        "teachers/teacher_leave_apply.html",
        {
            "form": form,
            "title": "Apply Leave",
        },
    )


# ==========================================================
# TEACHER LEAVE REQUESTS
# ==========================================================

@login_required
def teacher_leave_requests(request):

    leaves = Leave.objects.filter(
        applicant=request.user
    ).order_by(
        "-applied_at"
    )

    paginator = Paginator(
        leaves,
        10,
    )

    leaves = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "teachers/teacher_leave_list.html",
        {
            "leaves": leaves,
            "title": "My Leave Requests",
        },
    )


# ==========================================================
# TEACHER ANNOUNCEMENTS
# ==========================================================

@login_required
def teacher_announcements(request):

    announcements = Announcement.objects.filter(
        target__in=[
            "ALL",
            "TEACHER",
        ]
    ).order_by(
        "-created_at"
    )

    paginator = Paginator(
        announcements,
        10,
    )

    announcements = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "teachers/teacher_announcements.html",
        {
            "announcements": announcements,
            "title": "Announcements",
        },
    )


# ==========================================================
# TEACHER NOTIFICATIONS
# ==========================================================

@login_required
def teacher_notifications(request):

    announcements = Announcement.objects.filter(
        target__in=[
            "ALL",
            "TEACHER",
        ]
    ).order_by(
        "-created_at"
    )[:20]

    return render(
        request,
        "teachers/teacher_notifications.html",
        {
            "notifications": announcements,
            "title": "Notifications",
        },
    )


# ==========================================================
# TEACHER CALENDAR
# ==========================================================

@login_required
def teacher_calendar(request):

    timetable = Timetable.objects.filter(
        teacher__user=request.user
    ).select_related(
        "course",
        "department",
    )

    return render(
        request,
        "teachers/teacher_calendar.html",
        {
            "events": timetable,
            "title": "Academic Calendar",
        },
    )


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@login_required
def teacher_change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            request.user,
            request.POST,
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user,
            )

            messages.success(
                request,
                "Password changed successfully."
            )

            return redirect(
                "teacher_profile"
            )

    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(
        request,
        "teachers/teacher_changepassword.html",
        {
            "form": form,
            "title": "Change Password",
        },
    )
# ==========================================================
# IMPORT TEACHERS
# ==========================================================

@login_required
def import_teachers(request):

    if request.method == "POST":

        form = TeacherExcelImportForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            result = bulk_import_teachers(
                excel_file=form.cleaned_data["excel_file"],
                created_by=request.user,
            )

            request.session["teacher_credentials"] = result["credentials"]
            request.session["teacher_errors"] = result["errors"]

            messages.success(
                request,
                f"{result['success_count']} teachers imported successfully."
            )

            if result["error_count"] > 0:

                messages.warning(
                    request,
                    f"{result['error_count']} rows failed during import."
                )

            return redirect(
                "teacher_list"
            )

    else:

        form = TeacherExcelImportForm()

    return render(
        request,
        "teachers/import_teachers.html",
        {
            "form": form,
            "title": "Import Teachers",
        },
    )


# ==========================================================
# EXPORT TEACHERS (EXCEL)
# ==========================================================

@login_required
def export_teachers_excel(request):

    dataframe = export_teachers_excel_service(

        TeacherProfile.objects.select_related(
            "user",
            "department",
        )

    )

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:

        dataframe.to_excel(
            writer,
            index=False,
        )

    output.seek(0)

    response = HttpResponse(

        output.read(),

        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="teachers.xlsx"'

    return response


# ==========================================================
# EXPORT TEACHERS (CSV)
# ==========================================================

@login_required
def export_teachers_csv(request):

    dataframe = export_teachers_csv_service(

        TeacherProfile.objects.select_related(
            "user",
            "department",
        )

    )

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="teachers.csv"'

    dataframe.to_csv(
        response,
        index=False,
    )

    return response


# ==========================================================
# DOWNLOAD GENERATED CREDENTIALS
# ==========================================================

@login_required
def download_credentials(request):

    credentials = request.session.get(
        "teacher_credentials",
        [],
    )

    dataframe = export_credentials(
        credentials
    )

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="teacher_credentials.csv"'

    dataframe.to_csv(
        response,
        index=False,
    )

    return response


# ==========================================================
# DOWNLOAD ERROR REPORT
# ==========================================================

@login_required
def download_error_report(request):

    errors = request.session.get(
        "teacher_errors",
        [],
    )

    dataframe = export_error_report(
        errors
    )

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="teacher_import_errors.csv"'

    dataframe.to_csv(
        response,
        index=False,
    )

    return response

# ==========================================================
# RESEND TEACHER CREDENTIALS
# ==========================================================

@login_required
@admin_required
def resend_teacher_credentials(request, pk):
    teacher = get_object_or_404(TeacherProfile.objects.select_related("user"), pk=pk)
    user = teacher.user

    if request.method == "POST":
        from django.utils.crypto import get_random_string
        from accounts.services import send_account_credentials_email

        new_temp_password = get_random_string(10)
        user.set_password(new_temp_password)
        user.must_change_password = True
        user.save()

        email_ok, email_err = send_account_credentials_email(
            user, new_temp_password, role="TEACHER", request=request
        )

        if email_ok:
            messages.success(
                request,
                f"New login credentials have been sent to {user.email}."
            )
        else:
            messages.warning(
                request,
                f"Credentials were regenerated, but the email could not be sent to {user.email}. (Error: {email_err})"
            )

        return redirect("teacher_list")

    return render(
        request,
        "teachers/teacher_resend_confirm.html",
        {
            "teacher": teacher,
            "user_obj": user,
            "title": "Resend Teacher Credentials",
        },
    )
