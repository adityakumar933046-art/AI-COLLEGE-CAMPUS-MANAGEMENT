import csv
from openpyxl import Workbook
def clean_query_param(val):
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str.lower() in ("", "none", "null", "undefined"):
        return None
    return val_str

from accounts.decorators import admin_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.core.paginator import Paginator

from django.db.models import Q

from django.http import HttpResponse


from .models import StudentProfile


from .forms import (
    StudentCreateForm,
    StudentUpdateForm,
    StudentExcelImportForm,
)


from .services import (
    create_student,
    update_student,
    delete_student as delete_student_service,

    activate_student,
    deactivate_student,

    bulk_import_students,

    export_students_excel,
    export_students_csv,

    generate_student_sample_excel,
    generate_error_report,
)




# ==========================================================
# STUDENT LIST
# ==========================================================

@login_required
@staff_member_required
def student_list(request):


    students = StudentProfile.objects.select_related(
        "user",
        "department"
    ).order_by(
        "roll_no"
    )
    


    search = request.GET.get(
        "search",
        ""
    )


    department = request.GET.get(
        "department",
        ""
    )


    semester = request.GET.get(
        "semester",
        ""
    )


    status = request.GET.get(
        "status",
        ""
    )



    if search:


        students = students.filter(

            Q(roll_no__icontains=search)

            |
            Q(admission_no__icontains=search)

            |
            Q(user__username__icontains=search)

            |
            Q(user__first_name__icontains=search)

            |
            Q(user__last_name__icontains=search)

            |
            Q(user__email__icontains=search)

        )



    if department:

        students = students.filter(
            department_id=department
        )



    if semester:

        students = students.filter(
            semester=semester
        )



    if status:

        students = students.filter(
            status=status
        )



    paginator = Paginator(
        students,
        20
    )


    page = request.GET.get(
        "page"
    )


    students = paginator.get_page(
        page
    )



    context = {


        "students": students,


        "search": search,


        "department": department,


        "semester": semester,


        "status": status,


        "total_students":
            StudentProfile.objects.count(),


        "active_students":
            StudentProfile.objects.filter(
                status="ACTIVE"
            ).count(),


        "inactive_students":
            StudentProfile.objects.filter(
                status="INACTIVE"
            ).count(),


    }



    return render(

        request,

        "students/student_list.html",

        context

    )






# ==========================================================
# STUDENT DETAIL
# ==========================================================

@login_required
@staff_member_required
def student_detail(request, pk):


    student = get_object_or_404(

        StudentProfile.objects.select_related(
            "user",
            "department"
        ),

        pk=pk

    )


    return render(

        request,

        "students/student_detail.html",

        {
            "student": student
        }

    )

# ==========================================================
# ADD STUDENT
# ==========================================================

@staff_member_required
@login_required
def add_student(request):


    if request.method == "POST":


        form = StudentCreateForm(

            request.POST,

            request.FILES

        )


        if form.is_valid():


            data = form.cleaned_data



            result = create_student(

                data=data,

                created_by=request.user

            )



            if result["success"]:
                from accounts.services import send_student_credentials_email
                user_obj = result["user"]
                temp_pwd = result["password"]
                
                email_sent, email_err = send_student_credentials_email(user_obj, temp_pwd, request=request)
                
                if email_sent:
                    messages.success(
                        request,
                        f"Student account created successfully. Login credentials have been sent to {user_obj.email}."
                    )
                else:
                    messages.warning(
                        request,
                        f"Student account created successfully, but the credentials email could not be sent to {user_obj.email}. (Error: {email_err})"
                    )


                return redirect(
                    "student_list"
                )



            else:


                for error in result["errors"]:

                    messages.error(
                        request,
                        error
                    )



    else:


        form = StudentCreateForm()



    return render(

        request,

        "students/student_create.html",

        {

            "form": form,

            "title": "Add Student"

        }

    )





# ==========================================================
# UPDATE STUDENT
# ==========================================================

@staff_member_required
@login_required
def update_student(request, pk):

    student = get_object_or_404(
        StudentProfile,
        id=pk
    )


    if request.method == "POST":

        form = StudentUpdateForm(
            request.POST,
            request.FILES,
            instance=student
        )


        if form.is_valid():

            obj = form.save(commit=False)

            obj.updated_by = request.user

            obj.save()


            messages.success(
                request,
                "Student updated successfully."
            )


            return redirect(
                "student_detail",
                pk=student.id
            )


    else:

        form = StudentUpdateForm(
            instance=student
        )


    return render(
        request,
        "students/student_update.html",
        {
            "form": form,
            "student": student
        }
    )
# ==========================================================
# DELETE STUDENT
# ==========================================================

@staff_member_required
@login_required
def delete_student(request, pk):


    student = get_object_or_404(

        StudentProfile,

        pk=pk

    )


    if request.method == "POST":


        result = delete_student_service(student)


        if result["success"]:


            messages.success(

                request,

                "Student deleted successfully."

            )


            return redirect(
                "student_list"
            )


        else:


            for error in result["errors"]:

                messages.error(
                    request,
                    error
                )



    return render(

        request,

        "students/student_delete.html",

        {

            "student": student

        }

    )





# ==========================================================
# ACTIVATE STUDENT
# ==========================================================

@staff_member_required
@login_required
def activate_student_view(request, pk):


    student = get_object_or_404(

        StudentProfile,

        pk=pk

    )



    activate_student(

        student=student,

        user=request.user

    )


    messages.success(

        request,

        "Student activated successfully."

    )


    return redirect(

        "student_detail",

        pk=pk

    )





# ==========================================================
# DEACTIVATE STUDENT
# ==========================================================

@staff_member_required
@login_required
def deactivate_student_view(request, pk):


    student = get_object_or_404(

        StudentProfile,

        pk=pk

    )



    deactivate_student(

        student=student,

        user=request.user

    )


    messages.success(

        request,

        "Student deactivated successfully."

    )


    return redirect(

        "student_detail",

        pk=pk

    )





# ==========================================================
# STUDENT DASHBOARD
# ==========================================================

@staff_member_required
@login_required
def student_dashboard(request):


    total_students = StudentProfile.objects.count()



    active_students = StudentProfile.objects.filter(

        status="ACTIVE"

    ).count()



    inactive_students = StudentProfile.objects.filter(

        status="INACTIVE"

    ).count()



    graduated_students = StudentProfile.objects.filter(

        status="GRADUATED"

    ).count()



    recent_students = StudentProfile.objects.select_related(

        "user",

        "department"

    ).order_by(

        "-created_at"

    )[:10]



    context = {


        "total_students": total_students,


        "active_students": active_students,


        "inactive_students": inactive_students,


        "graduated_students": graduated_students,


        "recent_students": recent_students,


    }



    return render(

        request,

        "students/student_dashboard.html",

        context

    )

# ==========================================================
# IMPORT STUDENTS FROM EXCEL
# ==========================================================

@staff_member_required
@login_required
def import_students(request):


    if request.method == "POST":


        form = StudentExcelImportForm(

            request.POST,

            request.FILES

        )


        if form.is_valid():


            import pandas as pd


            excel_file = form.cleaned_data[
                "excel_file"
            ]


            try:


                df = pd.read_excel(
                    excel_file
                )


                records = df.to_dict(
                    orient="records"
                )


                result = bulk_import_students(

                    records=records,

                    import_batch="STUDENT_IMPORT"

                )


                request.session[
                    "student_credentials"
                ] = result.get(
                    "credentials",
                    []
                )


                request.session[
                    "student_errors"
                ] = result.get(
                    "errors",
                    []
                )



                messages.success(

                    request,

                    f"Imported: {result['success_count']} | Failed: {result['failed_count']}"

                )


                return redirect(
                    "student_list"
                )


            except Exception as e:


                messages.error(

                    request,

                    f"Import failed: {str(e)}"

                )


    else:


        form = StudentExcelImportForm()



    return render(

        request,

        "students/import_students.html",

        {

            "form": form

        }

    )






# ==========================================================
# DOWNLOAD CREDENTIALS EXCEL
# ==========================================================

@staff_member_required
@login_required
def download_credentials(request):


    credentials = request.session.get(

        "student_credentials",

        []

    )


    if not credentials:


        messages.warning(

            request,

            "No credentials available."

        )


        return redirect(
            "student_list"
        )



    file = generate_credentials_excel(

        credentials

    )


    response = HttpResponse(

        file,

        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )


    response[
        "Content-Disposition"
    ] = 'attachment; filename="Student_Credentials.xlsx"'



    return response





# ==========================================================
# DOWNLOAD ERROR REPORT
# ==========================================================

@staff_member_required
@login_required
def download_error_report(request):


    errors = request.session.get(

        "student_errors",

        []

    )


    if not errors:


        messages.warning(

            request,

            "No error report available."

        )


        return redirect(
            "student_list"
        )



    file = generate_error_report(

        errors

    )


    response = HttpResponse(

        file,

        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )


    response[
        "Content-Disposition"
    ] = 'attachment; filename="Student_Error_Report.xlsx"'



    return response





# ==========================================================
# DOWNLOAD SAMPLE EXCEL
# ==========================================================

@staff_member_required
@login_required
def download_sample_excel(request):


    file = generate_student_sample_excel()



    response = HttpResponse(

        file,

        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )


    response[
        "Content-Disposition"
    ] = 'attachment; filename="Student_Sample.xlsx"'



    return response





# ==========================================================
# EXPORT STUDENTS EXCEL
# ==========================================================

# ==========================================================
# EXPORT STUDENTS EXCEL & CSV
# ==========================================================

@login_required
def export_students_excel(request):
    students = StudentProfile.objects.select_related("user", "department").all()
    

    dept = clean_query_param(request.GET.get("department"))
    if dept and dept.isdigit():
        students = students.filter(department_id=int(dept))

    sem = clean_query_param(request.GET.get("semester"))
    if sem and sem.isdigit():
        students = students.filter(semester=int(sem))

    sec = clean_query_param(request.GET.get("section"))
    if sec:
        students = students.filter(section__iexact=sec)

    search = clean_query_param(request.GET.get("search"))
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(roll_no__icontains=search) |
            Q(user__email__icontains=search)
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Students Roster"

    ws.append(["Roll Number", "First Name", "Last Name", "Email", "Department", "Semester", "Section", "Gender", "Phone Number"])

    for s in students.order_by("roll_no"):
        ws.append([
            s.roll_no,
            s.user.first_name if s.user else "",
            s.user.last_name if s.user else "",
            s.user.email if s.user else "",
            s.department.name if s.department else "N/A",
            s.semester,
            s.section,
            s.gender,
            getattr(s, 'phone', getattr(s, 'phone_number', '')),
        ])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="student_roster_report.xlsx"'
    wb.save(response)
    return response


@login_required
def export_students_csv(request):
    students = StudentProfile.objects.select_related("user", "department").all()
    

    dept = clean_query_param(request.GET.get("department"))
    if dept and dept.isdigit():
        students = students.filter(department_id=int(dept))

    sem = clean_query_param(request.GET.get("semester"))
    if sem and sem.isdigit():
        students = students.filter(semester=int(sem))

    sec = clean_query_param(request.GET.get("section"))
    if sec:
        students = students.filter(section__iexact=sec)

    search = clean_query_param(request.GET.get("search"))
    if search:
        students = students.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(roll_no__icontains=search) |
            Q(user__email__icontains=search)
        )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="student_roster_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Roll Number", "First Name", "Last Name", "Email", "Department", "Semester", "Section", "Gender", "Phone Number"])

    for s in students.order_by("roll_no"):
        writer.writerow([
            s.roll_no,
            s.user.first_name if s.user else "",
            s.user.last_name if s.user else "",
            s.user.email if s.user else "",
            s.department.name if s.department else "N/A",
            s.semester,
            s.section,
            s.gender,
            getattr(s, 'phone', getattr(s, 'phone_number', '')),
        ])

    return response


# ==========================================================
# EXPORT STUDENTS CSV
# ==========================================================

@staff_member_required
@login_required
def export_students_csv(request):


    response = export_students_csv()


    return response

# ==========================================================
# STUDENT PROFILE VIEW
# ==========================================================

@login_required
def student_profile(request):
    return redirect("profile")


@login_required
@staff_member_required
def bulk_activate_students(request):

    if request.method == "POST":

        ids = request.POST.getlist("student_ids")


        students = StudentProfile.objects.filter(
            id__in=ids
        )


        count = students.update(
            status="ACTIVE",
            updated_by=request.user
        )


        messages.success(
            request,
            f"{count} students activated successfully."
        )


    return redirect(
        "student_list"
    )





# ==========================================================
# BULK DEACTIVATE STUDENTS
# ==========================================================

@login_required
@staff_member_required
def bulk_deactivate_students(request):

    if request.method == "POST":

        ids = request.POST.getlist("student_ids")


        students = StudentProfile.objects.filter(
            id__in=ids
        )


        count = students.update(
            status="INACTIVE",
            updated_by=request.user
        )


        messages.success(
            request,
            f"{count} students deactivated successfully."
        )


    return redirect(
        "student_list"
    )

# ==========================================================
# RESEND STUDENT CREDENTIALS
# ==========================================================

@login_required
@admin_required
def resend_student_credentials(request, pk):
    student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=pk)
    user = student.user

    if request.method == "POST":
        from django.utils.crypto import get_random_string
        from accounts.services import send_account_credentials_email

        new_temp_password = get_random_string(10)
        user.set_password(new_temp_password)
        user.must_change_password = True
        user.save()

        email_ok, email_err = send_account_credentials_email(
            user, new_temp_password, role="STUDENT", request=request
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

        return redirect("student_list")

    return render(
        request,
        "students/student_resend_confirm.html",
        {
            "student": student,
            "user_obj": user,
            "title": "Resend Student Credentials",
        },
    )
