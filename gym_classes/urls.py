from django.urls import path
from . import views

app_name = 'gym_classes'

urlpatterns = [
    path('', views.agresso, name='agresso'),
    path('class_manager/', views.class_manager, name='class_manager'),
    path('content_manager/', views.content_manager, name='content_manager'),
    ]
