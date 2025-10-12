# main/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='home'),  # root URL
    path('login/', views.login_view, name='login'),
    # path('login/', views.student_login, name='login'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('studentdashboard/', views.student_dashboard, name='student_dashboard'),
    path('update-password/', views.update_password, name='update_password'),
    path('student-profile/', views.student_profile, name='student_profile'),
    path('studentlogin/', views.student_login, name='student_login'),
    path('signup/', views.student_signup, name='signup'),
    path('signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.student_login, name='student_login'),
    # path('signup/', views.student_signup, name='student_signup'),

    path('organizerdashboard/', views.organizer_dashboard, name='organizer_dashboard'),

    path('organizerlogin/', views.organizer_login, name='organizer_login'),

    path('update-organizer-profile/', views.update_organizer_profile, name='update_organizer_profile'),

    path('organizer-signup/', views.organizer_signup, name='organizer_signup'),
    




]
