from django.urls import path
from . import views

urlpatterns = [

    # ==========================================
    # ADMIN LEAVE LIST
    # ==========================================

    path(
        '',
        views.leave_list,
        name='leave_list'
    ),

    # ==========================================
    # MY LEAVES
    # ==========================================

    path(
        'my/',
        views.my_leaves,
        name='my_leaves'
    ),

    # ==========================================
    # APPLY LEAVE
    # ==========================================

    path(
        'apply/',
        views.apply_leave,
        name='apply_leave'
    ),

    # ==========================================
    # LEAVE DETAIL
    # ==========================================

    path(
        '<int:pk>/',
        views.leave_detail,
        name='leave_detail'
    ),

    # ==========================================
    # UPDATE STATUS
    # ==========================================

    path(
        '<int:pk>/update/',
        views.update_leave_status,
        name='update_leave_status'
    ),

    # ==========================================
    # APPROVE LEAVE
    # ==========================================

    path(
        '<int:pk>/approve/',
        views.approve_leave,
        name='approve_leave'
    ),

    # ==========================================
    # REJECT LEAVE
    # ==========================================

    path(
        '<int:pk>/reject/',
        views.reject_leave,
        name='reject_leave'
    ),

    # ==========================================
    # DELETE LEAVE
    # ==========================================

    path(
        '<int:pk>/delete/',
        views.delete_leave,
        name='delete_leave'
    ),

]