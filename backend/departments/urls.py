from django.urls import path

from . import views


urlpatterns = [

    # ==========================
    # DEPARTMENT CRUD
    # ==========================

    path(
        '',
        views.department_list,
        name='department_list'
    ),

    path(
        'create/',
        views.department_create,
        name='department_create'
    ),

    path(
        '<int:pk>/',
        views.department_detail,
        name='department_detail'
    ),

    path(
        '<int:pk>/update/',
        views.department_update,
        name='department_update'
    ),

    path(
        '<int:pk>/delete/',
        views.department_delete,
        name='department_delete'
    ),


    # ==========================
    # STATUS MANAGEMENT
    # ==========================

    path(
        '<int:pk>/activate/',
        views.activate_department_view,
        name='activate_department'
    ),

    path(
        '<int:pk>/deactivate/',
        views.deactivate_department_view,
        name='deactivate_department'
    ),

    path(
        '<int:pk>/toggle/',
        views.toggle_department_status_view,
        name='toggle_department_status'
    ),


    # ==========================
    # EXCEL IMPORT
    # ==========================

    path(
        'import/',
        views.import_departments,
        name='import_departments'
    ),


    # ==========================
    # EXPORT
    # ==========================

    path(
        'export/excel/',
        views.export_departments_excel_view,
        name='export_departments_excel'
    ),

    path(
        'export/csv/',
        views.export_departments_csv_view,
        name='export_departments_csv'
    ),


    # ==========================
    # SAMPLE & ERROR REPORT
    # ==========================

    path(
    "sample-excel/",
    views.download_sample_excel_view,
    name="download_department_sample",
),

    path(
        'error-report/',
        views.download_error_report_view,
        name='download_error_report'
    ),

]