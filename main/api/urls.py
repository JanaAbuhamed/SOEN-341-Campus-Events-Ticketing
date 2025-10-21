# main/api/urls.py
from django.urls import path
from . import views
from .qr_views import qr_png, qr_svg

urlpatterns = [
    # Student ticket actions
    path("events/<int:event_id>/claim/",   views.claim_event,   name="claim_event"),
    path("events/<int:event_id>/unclaim/", views.unclaim_event, name="unclaim_event"),

    # QR for tickets
    path("events/<int:event_id>/qr.png", qr_png, name="ticket_qr_png"),
    path("events/<int:event_id>/qr.svg", qr_svg, name="ticket_qr_svg"),

    # Admin operations (existing)
    path("admin/users/create/",                     views.admin_create_user,         name="admin_create_user"),
    path("admin/events/create/",                    views.admin_create_event,        name="admin_create_event"),
    path("admin/events/<int:event_id>/status/",     views.admin_update_event_status, name="admin_update_event_status"),
    path("admin/events/<int:event_id>/edit/",       views.admin_edit_event,          name="admin_edit_event"),

    # NEW: inline + bulk
    path("admin/users/<int:user_id>/status/json/",  views.admin_user_set_status_json, name="admin_user_set_status_json"),
    path("admin/users/bulk/",                       views.admin_users_bulk,           name="admin_users_bulk"),
    path("admin/events/bulk/",                      views.admin_events_bulk,          name="admin_events_bulk"),
]
