from django.urls import path
from . import views
urlpatterns = [

    # ==========================================
    # TIMETABLE LIST
    # ==========================================

    path(
        '',
        views.timetable_list,
        name='timetable_list'
    ),

    # ==========================================
    # CREATE TIMETABLE
    # ==========================================

    path(
        'create/',
        views.timetable_create,
        name='timetable_create'
    ),

    # ==========================================
    # TIMETABLE DETAIL
    # ==========================================

    path(
        '<int:pk>/',
        views.timetable_detail,
        name='timetable_detail'
    ),

    # ==========================================
    # UPDATE TIMETABLE
    # ==========================================

    path(
        '<int:pk>/update/',
        views.timetable_update,
        name='timetable_update'
    ),

    # ==========================================
    # DELETE TIMETABLE
    # ==========================================

    path(
        '<int:pk>/delete/',
        views.timetable_delete,
        name='timetable_delete'
    ),

    # ==========================================
    # STUDENT TIMETABLE
    # ==========================================

    path(
        'student/',
        views.student_timetable,
        name='student_timetable'
    ),

    # ==========================================
    # TEACHER TIMETABLE
    # ==========================================

    path(
        'teacher/',
        views.teacher_timetable,
        name='teacher_timetable'
    ),
    path(
    "dashboard/",
    views.timetable_dashboard,
    name="timetable_dashboard",
),

path(
    "export/csv/",
    views.export_timetable_csv,
    name="export_timetable_csv",
),

path(
    "export/excel/",
    views.export_timetable_excel,
    name="export_timetable_excel",
),
# ==========================================
# IMPORT TIMETABLE
# ==========================================

path(
    "import/",
    views.import_timetable,
    name="import_timetable",
),

# ==========================================
# DOWNLOAD SAMPLE
# ==========================================

path(
    "download-sample/",
    views.download_timetable_sample,
    name="download_timetable_sample",
),

]