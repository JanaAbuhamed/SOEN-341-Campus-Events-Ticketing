from django.urls import path
from . import views
from .views import UserViewSet, EventViewSet


user_list = UserViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

user_detail = UserViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

event_list = EventViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

event_detail = EventViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

event_register = EventViewSet.as_view({
    'post': 'register'
})

event_unregister = EventViewSet.as_view({
    'post': 'unregister'
})


urlpatterns = [
    path('users/', user_list, name='user-list'),
    path('users/<int:pk>/', user_detail, name='user-detail'),

    path('events/', event_list, name='event-list'),
    path('events/<int:pk>/', event_detail, name='event-detail'),
    path('events/<int:pk>/register/', event_register, name='event-register'),
    path('events/<int:pk>/unregister/', event_unregister, name='event-unregister'),

    # pages 
    path("", views.loginindex, name="loginindex"),
    path("signup/", views.signup, name="signup"),
    path("studentlogin/", views.studentlogin, name="studentlogin"),
    path("organizerlogin/", views.organizerlogin, name="organizerlogin"),
    path("adminlogin/", views.adminlogin, name="adminlogin"),
    path("studentdashboard/", views.studentdashboard, name="studentdashboard"),
    path("organizerdashboard/", views.organizerdashboard, name="organizerdashboard"),
    path("admindashboard/", views.admindashboard, name="admindashboard"),
    path("eventlist/", views.EventList, name="EventList"),
    path("organizerpending/", views.organizerpending, name="organizerpending"),






]

