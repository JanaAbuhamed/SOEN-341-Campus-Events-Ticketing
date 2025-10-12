# main/urls.py - CORRECTED
from django.urls import path
from main.api.views import (
    loginindex, signup, studentlogin, organizerlogin, adminlogin,
    studentdashboard, organizerdashboard, admindashboard, 
    EventList, organizerpending,update_profile,update_password
)

urlpatterns = [
    path("", loginindex, name="loginindex"),                   
    path("signup/", signup, name="signup"),                   
    path("studentlogin/", studentlogin, name="studentlogin"),  
    path("organizerlogin/", organizerlogin, name="organizerlogin"),
    path("adminlogin/", adminlogin, name="adminlogin"),
    path("studentdashboard/", studentdashboard, name="studentdashboard"),
    path("organizerdashboard/", organizerdashboard, name="organizerdashboard"),
    path("admindashboard/", admindashboard, name="admindashboard"),
    path("eventlist/", EventList, name="EventList"),
    path("organizerpending/", organizerpending, name="organizerpending"),

       
    path("update-profile/", update_profile, name="update_profile"),
    path("update-password/", update_password, name="update_password"),

]
