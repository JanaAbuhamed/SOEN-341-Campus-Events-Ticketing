# main/urls.py

from django.urls import path
# from .views import organizer_dashboard as organizer_dashboard_view
from .views import organizer_dashboard, update_organizer_profile
from . import views
# from main.api.views import (
#     loginindex, signup, studentlogin, organizerlogin, adminlogin,
#     studentdashboard, organizerdashboard, admindashboard, 
#     EventList, organizerpending,update_profile,update_password
# )

from main.api.views import (
    loginindex, signup, studentlogin, organizerlogin, adminlogin,
    studentdashboard, admindashboard, 
    EventList, organizerpending, update_profile, update_password
)


urlpatterns = [
    path("", loginindex, name="loginindex"),                   
    path("signup/", signup, name="signup"),                   
    path("studentlogin/", studentlogin, name="studentlogin"),  
    path("organizerlogin/", organizerlogin, name="organizerlogin"),
    path("adminlogin/", adminlogin, name="adminlogin"),
    path("studentdashboard/", studentdashboard, name="studentdashboard"),

    # path("organizerdashboard/", organizer_dashboard_view, name="organizerdashboard"),
    
    path("organizerdashboard/", organizer_dashboard, name="organizerdashboard"),
    path("update-organizer-profile/", update_organizer_profile, name="update_organizer_profile"),

    path('edit-event/<int:event_id>/', views.edit_event, name='edit-event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete-event'),
    path("admindashboard/", admindashboard, name="admindashboard"),

    path("organizerpending/", organizerpending, name="organizerpending"),

       
    path("update-profile/", update_profile, name="update_profile"),
    path("update-password/", update_password, name="update_password"),

    
    path('organizer/edit-profile/', update_organizer_profile, name='update_organizer_profile'),
    # Event list HTML and API
    path('eventlist/', views.eventlist, name='eventlist'),
    path('api/events/', views.eventlist_api, name='eventlist_api'),
    # Event Registration API
path('api/events/<int:event_id>/register/', views.register_event, name='register_event'),
path('api/events/<int:event_id>/unregister/', views.unregister_event, name='unregister_event'),


path("studentcalendar/", views.student_calendar, name="student_calendar"),





]
