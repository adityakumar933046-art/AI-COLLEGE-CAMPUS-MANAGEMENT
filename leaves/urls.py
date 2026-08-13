from django.urls import path
from . import views

urlpatterns = [
    path('', views.leave_list, name='leave_list'),
    path('teacher/', views.teacher_leave_list, name='teacher_leave_list'),
    path('my/', views.my_leaves, name='my_leaves'),
    path('my-leaves/', views.my_leaves, name='my_leaves_alias'),
    path('apply/', views.apply_leave, name='apply_leave'),
    path('<int:pk>/', views.leave_detail, name='leave_detail'),
    path('<int:pk>/approve/', views.approve_leave, name='approve_leave'),
    path('<int:pk>/reject/', views.reject_leave, name='reject_leave'),
    path('<int:pk>/cancel/', views.cancel_leave, name='cancel_leave'),
    path('<int:pk>/certificate/', views.download_certificate, name='download_certificate'),
]
