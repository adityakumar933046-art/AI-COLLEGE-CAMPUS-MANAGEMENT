from django.urls import path
from . import views


urlpatterns = [

    # ==========================================
    # QR Session List
    # ==========================================

    path(
        '',
        views.qr_session_list,
        name='qr_session_list'
    ),

    # ==========================================
    # Create QR Session
    # ==========================================

    path(
        'create/',
        views.create_qr_session,
        name='create_qr_session'
    ),

    # ==========================================
    # QR Session Detail
    # ==========================================

    path(
        '<int:pk>/',
        views.qr_session_detail,
        name='qr_session_detail'
    ),

    # ==========================================
    # Refresh QR Every 10 Seconds
    # ==========================================

    path(
        '<int:pk>/refresh/',
        views.refresh_qr,
        name='refresh_qr'
    ),

    # ==========================================
    # Close QR Session
    # ==========================================

    path(
        '<int:pk>/close/',
        views.close_session,
        name='close_session'
    ),

    # ==========================================
    # Delete QR Session
    # ==========================================

    path(
        '<int:pk>/delete/',
        views.delete_session,
        name='delete_session'
    ),

    # ==========================================
    # Student Scan QR
    # ==========================================

    path(
        'scan/<uuid:token>/',
        views.scan_qr,
        name='scan_qr'
    ),

    # ==========================================
    # Live Attendance Count API
    # ==========================================

    path(
        '<int:pk>/attendance-count/',
        views.attendance_count,
        name='attendance_count'
    ),

]

