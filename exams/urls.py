from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('create/', views.exam_create, name='exam_create'),
    path('<int:pk>/', views.exam_detail, name='exam_detail'),
    path('<int:pk>/edit/', views.exam_update, name='exam_update'),
    path('<int:pk>/delete/', views.exam_delete, name='exam_delete'),
    path('<int:pk>/publish/', views.exam_publish, name='exam_publish'),
    path('<int:pk>/cancel/', views.exam_cancel, name='exam_cancel'),

    path('<int:exam_id>/schedule/create/', views.schedule_create, name='schedule_create'),
    path('schedule/<int:pk>/edit/', views.schedule_update, name='schedule_update'),
    path('schedule/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),

    path('my/', views.my_exams, name='my_exams'),
    path('duties/', views.my_exam_duties, name='my_exam_duties'),

    path('<int:exam_id>/export/excel/', views.export_exam_schedule_excel, name='export_exam_schedule_excel'),
    path('<int:exam_id>/export/csv/', views.export_exam_schedule_csv, name='export_exam_schedule_csv'),
]
