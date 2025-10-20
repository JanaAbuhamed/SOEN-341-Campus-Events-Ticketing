# main/api/qr_views.py
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404

from ..models import Event

# PNG generation
import qrcode

# SVG generation
from qrcode.image.svg import SvgImage


def _ensure_ticket_owner(user, event_id):
    """
    Only allow a student who claimed the event (or an admin) to fetch its QR.
    """
    event = get_object_or_404(Event, id=event_id)

    # Admins can fetch for anything
    if getattr(user, "role", None) == 2:
        return event

    # Students must have claimed the ticket
    if not user.is_authenticated or getattr(user, "role", None) != 0:
        raise HttpResponseForbidden("Students only.")

    if not event.attendees.filter(pk=user.pk).exists():
        # Not your ticket
        raise Http404("Ticket not found.")

    return event


@login_required
def qr_png(request, event_id: int):
    """
    Return a PNG QR for a claimed ticket.
    """
    event = _ensure_ticket_owner(request.user, event_id)
    payload = f"TICKET|event:{event.id}|user:{request.user.pk}"

    img = qrcode.make(payload)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")


@login_required
def qr_svg(request, event_id: int):
    """
    Return an SVG QR for a claimed ticket.
    """
    event = _ensure_ticket_owner(request.user, event_id)
    payload = f"TICKET|event:{event.id}|user:{request.user.pk}"

    img = qrcode.make(payload, image_factory=SvgImage)
    buf = BytesIO()
    img.save(buf)
    return HttpResponse(buf.getvalue(), content_type="image/svg+xml")
