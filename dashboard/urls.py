from django.urls import path
from . import views
from attendance import views as attendance_views
from courses import views as course_views
from timetable import views as timetable_views

urlpatterns = [
    path("api/analytics/", views.analytics_api, name="analytics_api"),
    path("", views.dashboard_redirect, name="dashboard_redirect"),
    path("", views.dashboard_redirect, name="home"),

    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("student/", views.student_dashboard, name="student_dashboard"),

    path("profile/", views.dashboard_profile, name="dashboard_profile"),
    path("notifications/", views.dashboard_notifications, name="notifications"),
    
    path("calendar/", views.dashboard_calendar, name="calendar"),
    path("calendar/create/", views.calendar_event_create, name="calendar_event_create"),
    path("calendar/<int:pk>/edit/", views.calendar_event_update, name="calendar_event_update"),
    path("calendar/<int:pk>/delete/", views.calendar_event_delete, name="calendar_event_delete"),

    path("activity/", views.recent_activity, name="activity"),
    path("quick-links/", views.quick_links, name="quick_links"),
    path("about/", views.about, name="about"),

    # Student Module Aliases
    path("student/courses/", course_views.student_courses, name="student_courses"),
    path("student/attendance/", attendance_views.student_attendance, name="student_attendance"),
    path("student/results/", views.student_results, name="student_results"),
    path("student/assignments/", views.student_assignments, name="student_assignments"),
    path("student/notes/", views.student_notes, name="student_notes"),
    path("student/timetable/", timetable_views.student_timetable, name="student_timetable"),
    path("student/leaves/", views.student_leaves, name="student_leaves"),
    path("student/announcements/", views.student_announcements, name="student_announcements"),
]
