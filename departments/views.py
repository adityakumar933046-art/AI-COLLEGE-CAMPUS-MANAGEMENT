from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required

from .forms import (
    DepartmentForm,
    DepartmentExcelImportForm,
)

from .models import Department

from .services import (
    create_department,
    update_department,
    delete_department,

    activate_department,
    deactivate_department,
    toggle_department_status,

    bulk_import_departments,

    export_departments_excel,
    export_departments_csv,

    download_error_report,
    download_sample_excel,
)


# ==========================================================
# DEPARTMENT LIST
# ==========================================================

@login_required
@admin_required
def department_list(request):

    departments = Department.objects.select_related(
        "hod"
    ).order_by("name")

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:

        departments = departments.filter(

            Q(code__icontains=search) |
            Q(name__icontains=search) |
            Q(short_name__icontains=search) |
            Q(hod__user__first_name__icontains=search) |
            Q(hod__user__last_name__icontains=search)

        )

    if status:

        departments = departments.filter(
            status=status
        )

    paginator = Paginator(
        departments,
        10
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        "page_obj": page_obj,
        "departments": page_obj,

        "search": search,
        "status": status,

        "total_departments": Department.objects.count(),

        "active_departments": Department.objects.filter(
            status="ACTIVE"
        ).count(),

        "inactive_departments": Department.objects.filter(
            status="INACTIVE"
        ).count(),

    }

    return render(
        request,
        "departments/department_list.html",
        context,
    )


# ==========================================================
# DEPARTMENT DETAIL
# ==========================================================

@login_required
@admin_required
def department_detail(request, pk):

    department = get_object_or_404(
        Department.objects.select_related("hod"),
        pk=pk,
    )

    context = {
        "department": department,
    }

    return render(
        request,
        "departments/department_detail.html",
        context,
    )
# ==========================================================
# CREATE DEPARTMENT
# ==========================================================

@login_required
@admin_required
def department_create(request):

    if request.method == "POST":

        form = DepartmentForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            create_department(
                form=form,
                user=request.user,
            )

            messages.success(
                request,
                "Department created successfully.",
            )

            return redirect(
                "department_list"
            )

    else:

        form = DepartmentForm()

    context = {

        "form": form,
        "title": "Add Department",
        "button_text": "Save Department",

    }

    return render(
        request,
        "departments/department_create.html",
        context,
    )


# ==========================================================
# UPDATE DEPARTMENT
# ==========================================================

@login_required
@admin_required
def department_update(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk,
    )

    if request.method == "POST":

        form = DepartmentForm(
            request.POST,
            request.FILES,
            instance=department,
        )

        if form.is_valid():

            update_department(
                form=form,
                user=request.user,
            )

            messages.success(
                request,
                "Department updated successfully.",
            )

            return redirect(
                "department_detail",
                pk=department.pk,
            )

    else:

        form = DepartmentForm(
            instance=department,
        )

    context = {

        "form": form,
        "department": department,
        "title": "Update Department",
        "button_text": "Update Department",

    }

    return render(
        request,
        "departments/department_update.html",
        context,
    )
# ==========================================================
# DELETE DEPARTMENT
# ==========================================================

@login_required
@admin_required
def department_delete(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk,
    )

    if request.method == "POST":

        delete_department(
            department=department,
        )

        messages.success(
            request,
            "Department deleted successfully.",
        )

        return redirect(
            "department_list"
        )

    return render(
        request,
        "departments/department_delete.html",
        {
            "department": department,
        },
    )


# ==========================================================
# ACTIVATE DEPARTMENT
# ==========================================================

@login_required
@admin_required
def activate_department_view(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk,
    )

    activate_department(
        department=department,
        user=request.user,
    )

    messages.success(
        request,
        "Department activated successfully.",
    )

    return redirect(
        "department_detail",
        pk=pk,
    )


# ==========================================================
# DEACTIVATE DEPARTMENT
# ==========================================================

@login_required
@admin_required
def deactivate_department_view(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk,
    )

    deactivate_department(
        department=department,
        user=request.user,
    )

    messages.success(
        request,
        "Department deactivated successfully.",
    )

    return redirect(
        "department_detail",
        pk=pk,
    )


# ==========================================================
# TOGGLE DEPARTMENT STATUS
# ==========================================================

@login_required
@admin_required
def toggle_department_status_view(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk,
    )

    toggle_department_status(
        department=department,
        user=request.user,
    )

    messages.success(
        request,
        "Department status updated successfully.",
    )

    return redirect(
        "department_detail",
        pk=pk,
    )
# ==========================================================
# IMPORT DEPARTMENTS FROM EXCEL
# ==========================================================

@login_required
@admin_required
def import_departments(request):

    if request.method == "POST":

        form = DepartmentExcelImportForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            result = bulk_import_departments(
                excel_file=form.cleaned_data["excel_file"],
                user=request.user,
            )

            messages.success(
                request,
                (
                    f"Import Completed. "
                    f"Created: {result['created']} | "
                    f"Updated: {result['updated']} | "
                    f"Skipped: {result['skipped']}"
                ),
            )

            if result["errors"]:

                request.session["department_import_errors"] = result["errors"]

                messages.warning(
                    request,
                    "Some rows could not be imported. "
                    "Download the error report.",
                )

            return redirect(
                "department_list"
            )

    else:

        form = DepartmentExcelImportForm()

    context = {

        "form": form,

        "title": "Import Departments",

    }

    return render(
        request,
        "departments/import_departments.html",
        context,
    )
# ==========================================================
# EXPORT DEPARTMENTS TO EXCEL
# ==========================================================

@login_required
@admin_required
def export_departments_excel_view(request):

    return export_departments_excel()


# ==========================================================
# EXPORT DEPARTMENTS TO CSV
# ==========================================================

@login_required
@admin_required
def export_departments_csv_view(request):

    return export_departments_csv()


# ==========================================================
# DOWNLOAD SAMPLE EXCEL
# ==========================================================

@login_required
@admin_required
def download_sample_excel_view(request):

    return download_sample_excel()


# ==========================================================
# DOWNLOAD IMPORT ERROR REPORT
# ==========================================================

@login_required
@admin_required
def download_error_report_view(request):

    error_rows = request.session.get(
        "department_import_errors",
        [],
    )

    if not error_rows:

        messages.warning(
            request,
            "No import error report available.",
        )

        return redirect(
            "department_list",
        )

    request.session.pop(
        "department_import_errors",
        None,
    )

    return download_error_report(
        error_rows,
    )