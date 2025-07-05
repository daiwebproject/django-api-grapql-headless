# api/urls.py
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.health_check, name='health_check'),
    path('status/', views.api_status, name='api_status'),
    path('info/', views.api_info, name='api_info'),
]