# student_event/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # All HTML pages (login, dashboards, event list, etc.)
    path("", include("main.urls")),

    # Pure API endpoints (claim/unclaim, admin approvals, stats)
    path("api/", include("main.api.urls")),
]
