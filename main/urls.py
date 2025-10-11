# main/urls.py

#might delete
from django.urls import path
from . import views

urlpatterns = [
    path('studentdashboard/', views.student_dashboard, name='student_dashboard'),
]
