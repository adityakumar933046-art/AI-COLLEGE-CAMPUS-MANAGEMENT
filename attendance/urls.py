from django.urls import path

from . import views

urlpatterns = [

    # ==========================================
    # DASHBOARD
    # ==========================================

    path(
        "dashboard/",
        views.attendance_dashboard,
        name="attendance_dashboard",
    ),

    # ==========================================
    # ATTENDANCE SESSION
    # ==========================================
    path(
    "take/<int:timetable_id>/",
    views.take_attendance_from_timetable,
    name="take_attendance_from_timetable",
),
    path(
        "",
        views.attendance_session_list,
        name="attendance_session_list"),
    path("list/", views.attendance_session_list, name="attendance_list"
    ),

    path(
        "create/",
        views.create_attendance_session,
        name="create_attendance_session",
    ),

    path(
        "<int:session_id>/mark/",
        views.mark_attendance,
        name="mark_attendance",
    ),

    path(
        "<int:session_id>/save/",
        views.save_attendance,
        name="save_attendance",
    ),

    # ==========================================
    # ATTENDANCE RECORDS
    # ==========================================

    path(
        "history/",
        views.attendance_history,
        name="attendance_history",
    ),

    path(
        "<int:pk>/detail/",
        views.attendance_detail,
        name="attendance_detail",
    ),

    path(
        "<int:pk>/update/",
        views.attendance_update,
        name="attendance_update",
    ),

    path(
        "<int:pk>/delete/",
        views.attendance_delete,
        name="attendance_delete",
    ),

    # ==========================================
    # STUDENT
    # ==========================================

    path(
        "student/",
        views.student_attendance,
        name="student_attendance",
    ),

    # ==========================================
    # REPORTS
    # ==========================================

    path(
        "defaulters/",
        views.attendance_defaulters,
        name="attendance_defaulters",
    ),

path(
    "export/excel/",
    views.export_attendance_excel,
    name="export_attendance_excel",
),

path(
    "export/csv/",
    views.export_attendance_csv,
    name="export_attendance_csv",
),
]