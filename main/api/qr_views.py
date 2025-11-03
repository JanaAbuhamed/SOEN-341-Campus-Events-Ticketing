# main/api/qr_views.py
from io import BytesIO
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie  # <-- NEW

from ..models import Event, Ticket

# PNG/SVG generation
import qrcode
from qrcode.image.svg import SvgImage


def _public_ticket_url(request, token: str) -> str:
    path = reverse("public_ticket_page", args=[token])
    return request.build_absolute_uri(path)


def _get_student_ticket_or_404(user, event_id: int):
    """
    Returns (event, ticket) for the logged-in student, or raises.

    NOTE: We restrict PNG/SVG generation to the student who actually owns
    the ticket (role=0). Admins aren’t expected to download student QR codes
    from here, so we don’t special-case them.
    """
    event = get_object_or_404(Event, id=event_id)

    # Student (owner)
    if not user.is_authenticated or getattr(user, "role", None) != 0:
        raise PermissionDenied("Students only")
    ticket = Ticket.objects.filter(event=event, user=user).first()
    if not ticket:
        raise Http404("Ticket not found")
    return event, ticket


@login_required
def qr_png(request, event_id: int):
    """
    Return a PNG QR for the student's claimed ticket.
    """
    _, ticket = _get_student_ticket_or_404(request.user, event_id)

    if not ticket.qr_token:
        ticket.mark_claimed()
        ticket.save(update_fields=["claimed_at", "qr_token"])

    url = _public_ticket_url(request, ticket.qr_token)
    img = qrcode.make(url)  # Pillow required
    buf = BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")


@login_required
def qr_svg(request, event_id: int):
    """
    Return an SVG QR for the student's claimed ticket.
    """
    _, ticket = _get_student_ticket_or_404(request.user, event_id)

    if not ticket.qr_token:
        ticket.mark_claimed()
        ticket.save(update_fields=["claimed_at", "qr_token"])

    url = _public_ticket_url(request, ticket.qr_token)
    img = qrcode.make(url, image_factory=SvgImage)
    buf = BytesIO()
    img.save(buf)
    return HttpResponse(buf.getvalue(), content_type="image/svg+xml")


# ---------- Public ticket landing (what phone cameras open) ----------
@require_GET
@transaction.atomic
def public_ticket_page(request, qr_token: str):
    """
    Anyone can open this. We record a scan (with mild de-duplication)
    and render a minimal HTML ticket view (no login required).
    """
    ticket = (
        Ticket.objects
        .select_related("event", "user")
        .filter(qr_token=qr_token)
        .first()
    )
    if not ticket:
        return render(request, "public_ticket_invalid.html", status=404)

    now = timezone.now()
    if not ticket.last_scanned_at or (now - ticket.last_scanned_at) > timedelta(seconds=3):
        ticket.record_scan()
        ticket.save(update_fields=["first_scanned_at", "last_scanned_at", "scan_count"])

    ctx = {
        "event": ticket.event,
        "ticket": ticket,
        "student_name": ticket.user.name,
    }
    return render(request, "public_ticket_valid.html", ctx)


# ---------- Organizer/Admin: check-in endpoint ----------
@login_required
@require_POST
@transaction.atomic
def qr_checkin_api(request):
    """
    POST body: token=<qr_token>
    Only Organizer (role=1) or Admin (role=2).
    Marks the ticket as checked in and returns brief details.
    """
    role = getattr(request.user, "role", None)
    if role not in (1, 2):
        return JsonResponse({"error": "Organizer or Admin required"}, status=403)

    # Accept either form-encoded or raw body "token=..."
    token = (request.POST.get("token") or "").strip()
    if not token and request.body:
        raw = request.body.decode(errors="ignore")
        token = raw.replace("token=", "").strip()

    ticket = (
        Ticket.objects
        .select_related("event", "user")
        .filter(qr_token=token)
        .first()
    )
    if not ticket:
        return JsonResponse({"ok": False, "message": "Invalid ticket"}, status=404)

    # If organizer, ensure they own the event
    if role == 1 and ticket.event.organizer_id != request.user.user_id:
        return JsonResponse({"error": "Not your event"}, status=403)

    already_checked = bool(ticket.checked_in_at)
    if not already_checked:
        ticket.mark_checked_in()
        ticket.save(update_fields=["checked_in_at"])

    return JsonResponse({
        "ok": True,
        "event_id": ticket.event.id,
        "event_title": ticket.event.title,
        "user_id": ticket.user.user_id,
        "student_name": ticket.user.name,
        "claimed_at": ticket.claimed_at,
        "first_scanned_at": ticket.first_scanned_at,
        "last_scanned_at": ticket.last_scanned_at,
        "scan_count": ticket.scan_count,
        "checked_in_at": ticket.checked_in_at,
        "already_checked_in": already_checked,
    })


# ---------- Event stats for organizer/admin dashboards ----------
@login_required
@require_GET
def event_stats_api(request, event_id: int):
    """
    Returns claimed, scanned, checked-in counts + first/last scan timestamps.
    Organizer can only see their events; Admin can see all.
    """
    role = getattr(request.user, "role", None)
    event = get_object_or_404(Event, pk=event_id)

    if role == 1 and event.organizer_id != request.user.user_id:
        return JsonResponse({"error": "Not your event"}, status=403)

    qs = Ticket.objects.filter(event=event)
    claimed = qs.filter(claimed_at__isnull=False).count()
    scanned = qs.filter(first_scanned_at__isnull=False).count()
    checked_in = qs.filter(checked_in_at__isnull=False).count()

    first_scan = (
        qs.exclude(first_scanned_at__isnull=True)
          .order_by("first_scanned_at")
          .values_list("first_scanned_at", flat=True)
          .first()
    )
    last_scan = (
        qs.exclude(last_scanned_at__isnull=True)
          .order_by("-last_scanned_at")
          .values_list("last_scanned_at", flat=True)
          .first()
    )

    return JsonResponse({
        "event_id": event.id,
        "claimed": claimed,
        "scanned": scanned,
        "checked_in": checked_in,
        "first_scan_at": first_scan,
        "last_scan_at": last_scan,
        "capacity": event.capacity,
    })


# ---------- Organizer scan page (camera) ----------
@login_required
@ensure_csrf_cookie   # <-- NEW: guarantees csrftoken cookie on this page
def organizer_scan_page(request):
    role = getattr(request.user, "role", None)
    if role not in (1, 2):
        raise PermissionDenied("Organizer/Admin only")
    return render(request, "organizer_scan.html", {})
