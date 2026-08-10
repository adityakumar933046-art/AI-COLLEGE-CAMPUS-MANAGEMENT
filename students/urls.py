from django.urls import path
from . import views

urlpatterns = [

    # ==========================================================
    # STUDENT CRUD & LISTING
    # ==========================================================
    path("", views.student_list, name="student_list"),
    path("create/", views.student_create if hasattr(views, 'student_create') else views.add_student, name="student_create"),
    path("add/", views.add_student if hasattr(views, 'add_student') else views.student_create, name="add_student"),
    path("<int:pk>/", views.student_detail, name="student_detail"),
    path("<int:pk>/update/", views.update_student, name="update_student"),
    path("<int:pk>/edit/", views.update_student, name="student_update"),
    path("<int:pk>/delete/", views.delete_student, name="delete_student"),
    path("<int:pk>/resend-credentials/", views.resend_student_credentials, name="resend_student_credentials"),
    path("<int:pk>/remove/", views.delete_student, name="student_delete"),

    # ==========================================================
    # STATUS MANAGEMENT
    # ==========================================================
    path("<int:pk>/activate/", views.activate_student_view, name="activate_student"),
    path("<int:pk>/deactivate/", views.deactivate_student_view, name="deactivate_student"),

    # ==========================================================
    # STUDENT PROFILE
    # ==========================================================
    path("profile/", views.student_profile, name="student_profile"),

    # ==========================================================
    # EXCEL IMPORT & EXPORT
    # ==========================================================
    path("import/", views.import_students, name="import_students"),
    path("sample/", views.download_sample_excel, name="download_student_sample"),
    path("credentials/", views.download_credentials, name="download_credentials"),
    path("errors/", views.download_error_report, name="download_error_report"),
    path("export/excel/", views.export_students_excel, name="export_students_excel"),
    path("export/csv/", views.export_students_csv, name="export_students_csv"),

    # ==========================================================
    # BULK ACTIONS
    # ==========================================================
    path("bulk/activate/", views.bulk_activate_students, name="bulk_activate_students"),
    path("bulk/deactivate/", views.bulk_deactivate_students, name="bulk_deactivate_students"),
]
