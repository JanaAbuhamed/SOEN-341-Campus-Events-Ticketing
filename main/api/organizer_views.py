# main/api/organizer_views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render


@login_required
def organizer_scan(request):
    """
    Simple page that loads the camera scanner for organizers/admins only.
    """
    role = getattr(request.user, "role", None)
    if role not in (1, 2):  # 1=Organizer, 2=Admin
        return HttpResponseForbidden("Organizer or Admin only.")
    return render(request, "organizer_scan.html")
