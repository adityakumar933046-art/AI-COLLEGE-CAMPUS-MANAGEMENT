from django.urls import path
from . import views

urlpatterns = [

    # ==========================================
    # ANNOUNCEMENT LIST
    # ==========================================

    path(
        '',
        views.announcement_list,
        name='announcement_list'
    ),

    # ==========================================
    # CREATE ANNOUNCEMENT
    # ==========================================

    path(
        'create/',
        views.announcement_create,
        name='announcement_create'
    ),

    # ==========================================
    # ANNOUNCEMENT DETAIL
    # ==========================================

    path(
        '<int:pk>/',
        views.announcement_detail,
        name='announcement_detail'
    ),

    # ==========================================
    # UPDATE ANNOUNCEMENT
    # ==========================================

    path(
        '<int:pk>/update/',
        views.announcement_update,
        name='announcement_update'
    ),

    # ==========================================
    # DELETE ANNOUNCEMENT
    # ==========================================

    path(
        '<int:pk>/delete/',
        views.announcement_delete,
        name='announcement_delete'
    ),

    # ==========================================
    # MY ANNOUNCEMENTS
    # ==========================================

    path(
        'my/',
        views.my_announcements,
        name='my_announcements'
    ),

    # ==========================================
    # PUBLIC ANNOUNCEMENTS
    # ==========================================

    path(
        'public/',
        views.public_announcements,
        name='public_announcements'
    ),

]