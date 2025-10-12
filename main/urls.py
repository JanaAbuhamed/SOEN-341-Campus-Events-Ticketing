
from django.urls import path
from .views import organizer_dashboard as organizer_dashboard_view
from . import views
from main.api.views import (
    loginindex, signup, studentlogin, organizerlogin, adminlogin,
    studentdashboard, organizerdashboard, admindashboard, 
    EventList, organizerpending
)

urlpatterns = [
    path("", loginindex, name="loginindex"),                   
    path("signup/", signup, name="signup"),                   
    path("studentlogin/", studentlogin, name="studentlogin"),  
    path("organizerlogin/", organizerlogin, name="organizerlogin"),
    path("adminlogin/", adminlogin, name="adminlogin"),
    path("studentdashboard/", studentdashboard, name="studentdashboard"),
    path("organizerdashboard/", organizer_dashboard_view, name="organizerdashboard"),
    path('edit-event/<int:event_id>/', views.edit_event, name='edit-event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete-event'),
    path("admindashboard/", admindashboard, name="admindashboard"),
    path("eventlist/", EventList, name="EventList"),
    path("organizerpending/", organizerpending, name="organizerpending"),
]

