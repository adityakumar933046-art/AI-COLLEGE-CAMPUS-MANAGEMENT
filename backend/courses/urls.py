from django.urls import path

from . import views

urlpatterns = [

    # ==========================================
    # COURSE CRUD
    # ==========================================

    path(
        "",
        views.course_list,
        name="course_list",
    ),

    path(
        "create/",
        views.course_create,
        name="course_create",
    ),

    path(
        "<int:pk>/",
        views.course_detail,
        name="course_detail",
    ),

    path(
        "<int:pk>/update/",
        views.course_update,
        name="course_update",
    ),

    path(
        "<int:pk>/delete/",
        views.course_delete,
        name="course_delete",
    ),

    path(
        "<int:pk>/activate/",
        views.activate_course,
        name="activate_course",
    ),

    path(
        "<int:pk>/deactivate/",
        views.deactivate_course,
        name="deactivate_course",
    ),

    # ==========================================
    # STUDENT
    # ==========================================

    path(
        "student/",
        views.student_courses,
        name="student_courses",
    ),

    # ==========================================
    # COURSE MATERIALS
    # ==========================================

    path(
        "<int:course_id>/materials/",
        views.course_materials,
        name="course_materials",
    ),

    path(
        "materials/upload/",
        views.upload_course_material,
        name="upload_course_material",
    ),

    path(
        "materials/<int:pk>/delete/",
        views.delete_course_material,
        name="delete_course_material",
    ),

    # ==========================================
    # EXCEL IMPORT / EXPORT
    # ==========================================

    path(
        "import/",
        views.import_courses,
        name="import_courses",
    ),

    path(
        "export/excel/",
        views.export_courses_excel,
        name="export_courses_excel",
    ),

    path(
        "export/csv/",
        views.export_courses_csv,
        name="export_courses_csv",
    ),

    path(
        "sample/",
        views.download_course_sample,
        name="download_course_sample",
    ),

]