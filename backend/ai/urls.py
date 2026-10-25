from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_page, name='ai_chat'),
    path('chat/', views.chat_api, name='ai_chat_api'),
]
