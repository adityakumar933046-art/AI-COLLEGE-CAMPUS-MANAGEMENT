from django.urls import path
from . import views

urlpatterns = [

    # ==========================================================
    # DASHBOARD & PROFILE
    # ==========================================================
    path("dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("profile/", views.teacher_profile, name="teacher_profile"),
    path("change-password/", views.teacher_change_password, name="teacher_change_password"),

    # ==========================================================
    # TEACHER CRUD & LISTING
    # ==========================================================
    path("", views.teacher_list, name="teacher_list"),
    path("add/", views.add_teacher, name="add_teacher"),
    path("create/", views.add_teacher, name="teacher_create"),
    path("<int:pk>/", views.teacher_detail, name="teacher_detail"),
    path("<int:pk>/edit/", views.update_teacher, name="update_teacher"),
    path("<int:pk>/update/", views.update_teacher, name="teacher_update"),
    path("<int:pk>/delete/", views.delete_teacher, name="delete_teacher"),
    path("<int:pk>/resend-credentials/", views.resend_teacher_credentials, name="resend_teacher_credentials"),
    path("<int:pk>/remove/", views.delete_teacher, name="teacher_delete"),

    # ==========================================================
    # TEACHER ACADEMIC MODULES
    # ==========================================================
    path("courses/", views.teacher_courses, name="teacher_courses"),
    path("students/", views.teacher_students, name="teacher_students"),
    path("attendance/", views.teacher_attendance, name="teacher_attendance"),
    path("assignments/", views.teacher_assignments, name="teacher_assignments"),
    path("notes/", views.teacher_notes, name="teacher_notes"),
    path("results/", views.teacher_results, name="teacher_results"),
    path("timetable/", views.teacher_timetable, name="teacher_timetable"),
    path("calendar/", views.teacher_calendar, name="teacher_calendar"),
    path("announcements/", views.teacher_announcements, name="teacher_announcements"),
    path("notifications/", views.teacher_notifications, name="teacher_notifications"),

    # ==========================================================
    # LEAVE MANAGEMENT
    # ==========================================================
    path("leave/apply/", views.teacher_leave_apply, name="teacher_leave_apply"),
    path("leave/list/", views.teacher_leave_requests, name="teacher_leave_requests"),

    # ==========================================================
    # IMPORT / EXPORT
    # ==========================================================
    path("import/", views.import_teachers, name="import_teachers"),
    path("export/excel/", views.export_teachers_excel, name="export_teachers_excel"),
    path("export/csv/", views.export_teachers_csv, name="export_teachers_csv"),
    path("download-credentials/", views.download_credentials, name="download_credentials"),
    path("download-error-report/", views.download_error_report, name="download_error_report"),
]
