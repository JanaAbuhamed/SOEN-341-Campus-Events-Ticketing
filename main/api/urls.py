# main/api/urls
from django.urls import path
from . import views
from .views import UserViewSet, EventViewSet
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, EventViewSet

# router = DefaultRouter()
# router.register(r'users', UserViewSet, basename='user')
# router.register(r'events', EventViewSet, basename='event')

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
   # API routes
    path('users/', user_list, name='user-list'),
    path('users/<int:pk>/', user_detail, name='user-detail'),
    path('events/', event_list, name='event-list'),
    path('events/<int:pk>/', event_detail, name='event-detail'),
    path('events/<int:pk>/register/', event_register, name='event-register'),
    path('events/<int:pk>/unregister/', event_unregister, name='event-unregister'),
    

]

