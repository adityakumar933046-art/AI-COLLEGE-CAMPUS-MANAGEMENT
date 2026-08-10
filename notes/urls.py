from django.urls import path
from . import views

urlpatterns = [

    # ==========================================
    # NOTE LIST
    # ==========================================

    path(
        '',
        views.note_list,
        name='note_list'
    ),

    # ==========================================
    # CREATE NOTE
    # ==========================================

    path(
        'create/',
        views.note_create,
        name='note_create'
    ),

    # ==========================================
    # NOTE DETAIL
    # ==========================================

    path(
        '<int:pk>/',
        views.note_detail,
        name='note_detail'
    ),

    # ==========================================
    # UPDATE NOTE
    # ==========================================

    path(
        '<int:pk>/update/',
        views.note_update,
        name='note_update'
    ),

    # ==========================================
    # DELETE NOTE
    # ==========================================

    path(
        '<int:pk>/delete/',
        views.note_delete,
        name='note_delete'
    ),

    # ==========================================
    # DOWNLOAD NOTE
    # ==========================================

    path(
        '<int:pk>/download/',
        views.download_note,
        name='download_note'
    ),

    # ==========================================
    # MY NOTES (STUDENT)
    # ==========================================

    path(
        'my-notes/',
        views.my_notes,
        name='my_notes'
    ),

    # ==========================================
    # TEACHER NOTES
    # ==========================================

    path(
        'teacher-notes/',
        views.teacher_notes,
        name='teacher_notes'
    ),

]