from django.urls import path
from . import views

urlpatterns = [
    path('', views.result_list, name='result_list'),
    path('create/', views.result_create, name='result_create'),
    path('<int:pk>/', views.result_detail, name='result_detail'),
    path('<int:pk>/update/', views.result_update, name='result_update'),
    path('<int:pk>/delete/', views.result_delete, name='result_delete'),
    path('my-results/', views.my_results, name='my_results'),
    path('semester/<int:semester>/', views.semester_results, name='semester_results'),
    path('marksheet/<int:semester>/', views.marksheet, name='marksheet'),
    path('toppers/', views.toppers, name='toppers'),
]
