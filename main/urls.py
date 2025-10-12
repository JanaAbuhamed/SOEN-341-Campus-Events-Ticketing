from django.urls import path
from .views import organizer_dashboard
from . import views


urlpatterns = [
    path('dashboard/', organizer_dashboard, name='organizer-dashboard'),
    path('edit-event/<int:event_id>/', views.edit_event, name='edit-event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete-event'),
]