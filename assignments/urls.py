from django.urls import path
from . import views

urlpatterns = [

    # ==========================
    # Assignment
    # ==========================

    path(
        '',
        views.assignment_list,
        name='assignment_list'
    ),

    path(
        'create/',
        views.assignment_create,
        name='assignment_create'
    ),

    path(
        '<int:pk>/',
        views.assignment_detail,
        name='assignment_detail'
    ),

    path(
        '<int:pk>/update/',
        views.assignment_update,
        name='assignment_update'
    ),

    path(
        '<int:pk>/delete/',
        views.assignment_delete,
        name='assignment_delete'
    ),

    # ==========================
    # Student Submission
    # ==========================

    path(
        '<int:pk>/submit/',
        views.submit_assignment,
        name='submit_assignment'
    ),

    # ==========================
    # Teacher Submission List
    # ==========================

    path(
        'submissions/',
        views.submission_list,
        name='submission_list'
    ),

    path(
        'submissions/<int:pk>/marks/',
        views.update_marks,
        name='update_marks'
    ),

]