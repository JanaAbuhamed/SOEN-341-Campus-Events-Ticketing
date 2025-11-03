# main/urls.py
from django.urls import path

from . import views                              # organizer CRUD + organizer profile
from main.api import views as api_views          # page views (student/admin auth + pages)
from main.api import qr_views                    # QR endpoints (scanner, public, APIs)

urlpatterns = [
    # Public landing page (guests)
    path("",                    api_views.home,                    name="home"),

    # Entry & auth pages
    path("login/",              api_views.loginindex,              name="loginindex"),
    path("signup/",             api_views.signup,                  name="signup"),
    path("studentlogin/",       api_views.studentlogin,            name="studentlogin"),
    path("organizerlogin/",     api_views.organizerlogin,          name="organizerlogin"),
    path("adminlogin/",         api_views.adminlogin,              name="adminlogin"),

    # Dashboards / pages
    path("studentdashboard/",   api_views.studentdashboard,        name="studentdashboard"),
    path("organizerdashboard/", views.organizer_dashboard,         name="organizerdashboard"),
    path("admindashboard/",     api_views.admindashboard,          name="admindashboard"),
    path("organizerpending/",   api_views.organizerpending,        name="organizerpending"),

    # Student event finder/detail + save toggle
    path("eventlist/",                          api_views.EventList,        name="EventList"),
    path("events/<int:event_id>/",              api_views.EventDetail,      name="EventDetail"),
    path("events/<int:event_id>/save/",         api_views.ToggleSaveEvent,  name="ToggleSaveEvent"),

    # Student profile/password
    path("update-profile/",      api_views.update_profile,          name="update_profile"),
    path("update-password/",     api_views.update_password,         name="update_password"),

    # Organizer profile + event CRUD
    path("update-organizer-profile/", views.update_organizer_profile, name="update_organizer_profile"),
    path("edit-event/<int:event_id>/",   views.edit_event,              name="edit-event"),
    path("delete-event/<int:event_id>/", views.delete_event,            name="delete-event"),

    # CSV export route for organizers
    path("event/<int:event_id>/export/", views.export_attendees_csv,     name="export_event_csv"),

    # Ticket claim / unclaim / checkout
    path("events/<int:event_id>/claim/",     api_views.claim_event,       name="claim_event"),
    path("events/<int:event_id>/unclaim/",   api_views.unclaim_event,     name="unclaim_event"),
    path("events/<int:event_id>/checkout/",  api_views.checkout,          name="checkout"),

    # QR image(s) for student tickets
    path("tickets/<int:event_id>/qr.png",    qr_views.qr_png,             name="ticket_qr_png"),
    path("tickets/<int:event_id>/qr.svg",    qr_views.qr_svg,             name="ticket_qr_svg"),

    # NEW: Organizer scanner page + QR APIs + public ticket page + stats
    path("organizer/scan/",                  qr_views.organizer_scan_page, name="organizer_scan"),
    path("api/qr/checkin/",                  qr_views.qr_checkin_api,      name="qr_checkin_api"),
    path("t/<str:qr_token>/",                qr_views.public_ticket_page,  name="public_ticket_page"),
    path("api/events/<int:event_id>/stats/", qr_views.event_stats_api,     name="event_stats_api"),
]
