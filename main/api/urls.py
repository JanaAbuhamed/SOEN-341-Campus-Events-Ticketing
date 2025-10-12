from django.urls import path
from .views import UserViewSet, EventViewSet, MyClaimedTicketsView

# --- User endpoints (ViewSet -> as_view maps) ---
user_list = UserViewSet.as_view({'get': 'list', 'post': 'create'})
user_detail = UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})

# --- Event endpoints ---
event_list = EventViewSet.as_view({'get': 'list', 'post': 'create'})
event_detail = EventViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})
event_register = EventViewSet.as_view({'post': 'register'})
event_unregister = EventViewSet.as_view({'post': 'unregister'})

urlpatterns = [
    # Users
    path('users/', user_list, name='user-list'),
    path('users/<int:pk>/', user_detail, name='user-detail'),

    # Events
    path('events/', event_list, name='event-list'),
    path('events/<int:pk>/', event_detail, name='event-detail'),
    path('events/<int:pk>/register/', event_register, name='event-register'),
    path('events/<int:pk>/unregister/', event_unregister, name='event-unregister'),

    # Calendar feed of claimed tickets (FullCalendar format)
    path('my-claimed-events/', MyClaimedTicketsView.as_view(), name='my-claimed-events'),
]

from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    # ... your existing paths ...
    path('student/calendar/', TemplateView.as_view(
        template_name='studentcalendar.html'
    ), name='student-calendar'),
]

