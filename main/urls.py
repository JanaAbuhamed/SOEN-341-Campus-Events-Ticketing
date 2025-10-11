# main/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('update-profile/', views.update_profile, name='update_profile'),
    path('studentdashboard/', views.student_dashboard, name='student_dashboard'),
    path('update-password/', views.update_password, name='update_password'),

]


