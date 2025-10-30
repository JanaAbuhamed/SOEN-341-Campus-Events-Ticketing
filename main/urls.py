# main/urls.py
from django.urls import path
from . import views                              # organizer CRUD + organizer profile
from main.api import views as api_views          # page views in main.api.views
from main.api.qr_views import qr_png             # QR image

urlpatterns = [
    # Public landing page (guests)
    path("",                    api_views.home,            name="home"),

    # Entry & auth pages
    path("login/",              api_views.loginindex,      name="loginindex"),   # optional: keep old login index
    path("signup/",             api_views.signup,          name="signup"),
    path("studentlogin/",       api_views.studentlogin,    name="studentlogin"),
    path("organizerlogin/",     api_views.organizerlogin,  name="organizerlogin"),
    path("adminlogin/",         api_views.adminlogin,      name="adminlogin"),

    # Dashboards / pages
    path("studentdashboard/",   api_views.studentdashboard,  name="studentdashboard"),
    path("organizerdashboard/", views.organizer_dashboard,   name="organizerdashboard"),
    path("admindashboard/",     api_views.admindashboard,    name="admindashboard"),
    path("organizerpending/",   api_views.organizerpending,  name="organizerpending"),

    # Student event finder page
    path("eventlist/",          api_views.EventList,         name="EventList"),

    # Student event detail + save toggle
    path("events/<int:event_id>/",        api_views.EventDetail,      name="EventDetail"),
    path("events/<int:event_id>/save/",   api_views.ToggleSaveEvent,  name="ToggleSaveEvent"),

    # Student profile/password pages
    path("update-profile/",     api_views.update_profile,    name="update_profile"),
    path("update-password/",    api_views.update_password,   name="update_password"),

    # Organizer profile + event CRUD
    path("update-organizer-profile/", views.update_organizer_profile, name="update_organizer_profile"),
    path("edit-event/<int:event_id>/",   views.edit_event,            name="edit-event"),
    path("delete-event/<int:event_id>/", views.delete_event,          name="delete-event"),

    # Ticket claim / unclaim / QR routes
    path("events/<int:event_id>/claim/",     api_views.claim_event,   name="claim_event"),
    path("events/<int:event_id>/unclaim/",   api_views.unclaim_event, name="unclaim_event"),
    path("tickets/<int:event_id>/qr.png",    qr_png,                  name="ticket_qr"),
    path("events/<int:event_id>/checkout/",  api_views.checkout,      name="checkout"),
]
