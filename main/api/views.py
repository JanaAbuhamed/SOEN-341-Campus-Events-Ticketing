# main/api/views.py
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..forms import OrganizerSignupForm, PasswordUpdateForm, StudentSignupForm, UserUpdateForm
from ..models import Event, User
from .serializers import EventCreateSerializer, EventSerializer, UserSerializer
from .permissions import (
    CanCreateEvent, CanDeleteEvent, CanEditEvent, CanRegisterEvent, CanViewEvents, CanViewUsers
)

# -------------------------------
# Public pages / logins
# -------------------------------

def loginindex(request):
    return render(request, "loginindex.html")

@ensure_csrf_cookie
@csrf_protect
def organizerlogin(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        qs = User.objects.filter(email=email, role=1)
        if not qs.exists():
            return render(request, "organizerlogin.html",
                          {"error": "No organizer account found for this email. Please sign up first.",
                           "prefill_email": email}, status=200)
        org = qs.first()
        if org.status != 1:
            return render(request, "organizerlogin.html",
                          {"error": "Your organizer account is pending admin approval.",
                           "prefill_email": email}, status=200)
        user = authenticate(request, email=email, password=password)
        if user is None:
            return render(request, "organizerlogin.html",
                          {"error": "Incorrect password. Please try again.",
                           "prefill_email": email}, status=200)
        login(request, user)
        return redirect("organizerdashboard")
    return render(request, "organizerlogin.html")

@ensure_csrf_cookie
@csrf_protect
def adminlogin(request):
    if request.method == "POST":
        identifier = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        email = identifier.lower()
        qs = User.objects.filter(email=email, role=2)
        if not qs.exists():
            return render(request, "adminlogin.html",
                          {"error": "No admin account found for this email.",
                           "prefill_email": identifier}, status=200)
        user = authenticate(request, email=email, password=password)
        if user is None or user.role != 2:
            return render(request, "adminlogin.html",
                          {"error": "Incorrect password for this admin account.",
                           "prefill_email": identifier}, status=200)
        login(request, user)
        return redirect("admindashboard")
    return render(request, "adminlogin.html")

def organizerpending(request):
    return render(request, "organizer-pending.html")

# -------------------------------
# Admin dashboard + admin actions
# -------------------------------

@login_required
def admindashboard(request):
    if getattr(request.user, "role", None) != 2:
        return HttpResponseForbidden("Admin access required")

    tab = request.GET.get("tab", "events")
    students = User.objects.filter(role=0).order_by("created_at")
    organizers = User.objects.filter(role=1).order_by("name")
    events = Event.objects.all().select_related("organizer").order_by("-created_at")
    return render(request, "admindashboard.html", {
        "tab": tab, "students": students, "organizers": organizers, "events": events
    })

# ---- Create user / event (existing) ----

@login_required
@csrf_protect
def admin_create_user(request):
    if getattr(request.user, "role", None) != 2:
        return HttpResponseForbidden("Admin access required")
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    role = int(request.POST.get("role", "0"))
    status_val = int(request.POST.get("status", "1"))

    if not (name and email and password):
        messages.error(request, "All fields are required to create a user.")
        return redirect("/admindashboard/?tab=students")

    if User.objects.filter(email=email).exists():
        messages.error(request, "A user with this email already exists.")
        return redirect("/admindashboard/?tab=students")

    user = User.objects.create_user(email=email, name=name, password=password, role=role, status=status_val)
    try:
        group_name = "Student" if role == 0 else "Organizer" if role == 1 else "Administrator"
        user.groups.add(Group.objects.get(name=group_name))
    except Group.DoesNotExist:
        pass

    messages.success(request, "User created.")
    return redirect("/admindashboard/?tab=students")

@login_required
@csrf_protect
def admin_create_event(request):
    if getattr(request.user, "role", None) != 2:
        return HttpResponseForbidden("Admin access required")
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    organizer_id = request.POST.get("organizer_id")
    organizer = get_object_or_404(User, user_id=organizer_id, role=1)
    data = {
        "title": request.POST.get("title"),
        "description": request.POST.get("description"),
        "date": request.POST.get("date"),
        "time": request.POST.get("time"),
        "location": request.POST.get("location"),
        "capacity": request.POST.get("capacity"),
        "ticket_type": request.POST.get("ticket_type", "free"),
        "status": request.POST.get("status", "pending"),
    }
    if not all([data["title"], data["date"], data["time"], data["location"], data["capacity"]]):
        messages.error(request, "Please fill all required fields.")
        return redirect("/admindashboard/?tab=events")

    Event.objects.create(organizer=organizer, **data)
    messages.success(request, "Event created.")
    return redirect("/admindashboard/?tab=events")

# ---- Event approve/reject (kept, now responds JSON for AJAX too) ----

@login_required
@csrf_protect
def admin_update_event_status(request, event_id: int):
    if getattr(request.user, "role", None) != 2:
        return HttpResponseForbidden("Admin access required")
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    event = get_object_or_404(Event, id=event_id)
    new_status = request.POST.get("status")
    if new_status not in {"approved", "rejected", "pending", "draft"}:
        return JsonResponse({"error": "Invalid status"}, status=400)

    event.status = new_status
    event.save(update_fields=["status"])

    # JSON if AJAX; otherwise redirect
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "event_id": event.id, "status": event.status})
    messages.success(request, f"Event status set to {new_status}.")
    return redirect("/admindashboard/?tab=events")

@login_required
@csrf_protect
def admin_edit_event(request, event_id: int):
    if getattr(request.user, "role", None) != 2:
        return HttpResponseForbidden("Admin access required")

    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        event.title = request.POST.get("title") or event.title
        event.description = request.POST.get("description") or ""
        event.date = request.POST.get("date") or event.date
        event.time = request.POST.get("time") or event.time
        event.location = request.POST.get("location") or event.location
        event.capacity = int(request.POST.get("capacity") or event.capacity)
        event.ticket_type = request.POST.get("ticket_type") or event.ticket_type
        status_val = request.POST.get("status") or event.status
        if status_val in {"approved", "rejected", "pending", "draft"}:
            event.status = status_val
        org_id = request.POST.get("organizer_id")
        if org_id:
            organizer = get_object_or_404(User, user_id=org_id, role=1)
            event.organizer = organizer

        event.save()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Event updated.")
        return redirect("/admindashboard/?tab=events")

    return redirect("/admindashboard/?tab=events")

# ---- NEW: Inline status for user (AJAX) ----

@login_required
@csrf_protect
def admin_user_set_status_json(request, user_id: int):
    """AJAX: set user.status (0=pending, 1=active, 2=suspended)."""
    if getattr(request.user, "role", None) != 2:
        return JsonResponse({"error": "Admin access required"}, status=403)
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    user = get_object_or_404(User, pk=user_id)
    try:
        new_status = int(request.POST.get("status"))
        if new_status not in (0, 1, 2):
            raise ValueError
    except Exception:
        return JsonResponse({"error": "Invalid status"}, status=400)

    user.status = new_status
    user.save(update_fields=["status"])
    return JsonResponse({"ok": True, "user_id": user.user_id, "status": user.status})

# ---- NEW: BULK actions ----

@login_required
@csrf_protect
def admin_users_bulk(request):
    """Bulk approve/suspend/pending/delete students & organizers."""
    if getattr(request.user, "role", None) != 2:
        return JsonResponse({"error": "Admin access required"}, status=403)
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    ids = request.POST.getlist("ids[]") or request.POST.getlist("ids")
    action = request.POST.get("action")
    qs = User.objects.filter(user_id__in=ids, role__in=[0, 1])  # only students/organizers

    if action in {"activate", "suspend", "pending"}:
        mapping = {"activate": 1, "suspend": 2, "pending": 0}
        updated = qs.update(status=mapping[action])
        return JsonResponse({"ok": True, "updated": updated})
    elif action == "delete":
        # don’t allow deleting yourself
        qs = qs.exclude(pk=request.user.pk)
        deleted_count = qs.count()
        qs.delete()
        return JsonResponse({"ok": True, "deleted": deleted_count})

    return JsonResponse({"error": "Unknown action"}, status=400)

@login_required
@csrf_protect
def admin_events_bulk(request):
    """Bulk approve/reject/delete events."""
    if getattr(request.user, "role", None) != 2:
        return JsonResponse({"error": "Admin access required"}, status=403)
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    ids = request.POST.getlist("ids[]") or request.POST.getlist("ids")
    action = request.POST.get("action")
    qs = Event.objects.filter(id__in=ids)

    if action == "approve":
        updated = qs.update(status="approved")
        return JsonResponse({"ok": True, "updated": updated})
    elif action == "reject":
        updated = qs.update(status="rejected")
        return JsonResponse({"ok": True, "updated": updated})
    elif action == "delete":
        deleted = qs.count()
        qs.delete()
        return JsonResponse({"ok": True, "deleted": deleted})

    return JsonResponse({"error": "Unknown action"}, status=400)

# -------------------------------
# Sign up / student login
# -------------------------------

@ensure_csrf_cookie
@csrf_protect
def signup(request):
    if request.method == "POST":
        role = request.POST.get("role")
        form = StudentSignupForm(request.POST) if role == "student" else OrganizerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                group = Group.objects.get(name="Student" if role == "student" else "Organizer")
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
            login(request, user)
            request.session["user_role"] = role
            return redirect("studentdashboard" if role == "student" else "organizerpending")
    else:
        form = StudentSignupForm()
    return render(request, "signup.html", {"form": form})

@ensure_csrf_cookie
@csrf_protect
def studentlogin(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = authenticate(request, email=email, password=password)
        if user is not None and user.role == 0:
            login(request, user)
            return redirect("studentdashboard")
        return render(request, "studentlogin.html",
                      {"error": "Invalid credentials or not a student account", "prefill_email": email})
    return render(request, "studentlogin.html")

# -------------------------------
# Student area
# -------------------------------

@login_required
def studentdashboard(request):
    if getattr(request.user, "role", None) != 0:
        return HttpResponseForbidden("Student access required")
    tickets = Event.objects.filter(attendees=request.user).order_by("date", "time")
    return render(request, "studentdashboard.html", {"tickets": tickets})

@login_required
def update_profile(request):
    user = request.user
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("studentdashboard")
    else:
        form = UserUpdateForm(instance=user)
    return render(request, "update_profile.html", {"form": form})

@login_required
def update_password(request):
    form = None
    if request.method == "POST":
        form = PasswordUpdateForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Your password has been updated successfully!")
            return redirect("studentdashboard")
    if not form:
        form = PasswordUpdateForm(request.user)
    return render(request, "update_password.html", {"form": form})

@login_required
def EventList(request):
    if getattr(request.user, "role", None) != 0:
        return HttpResponseForbidden("Student access required")
    events = Event.objects.filter(status="approved").order_by("date", "time")
    my_event_ids = set(Event.objects.filter(attendees=request.user).values_list("id", flat=True))
    return render(request, "EventList.html", {"events": events, "my_event_ids": my_event_ids})

@login_required
@csrf_protect
def claim_event(request, event_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    if getattr(request.user, "role", None) != 0:
        return JsonResponse({"error": "Student access required"}, status=403)
    event = get_object_or_404(Event, id=event_id, status="approved")
    if event.attendees.count() >= event.capacity:
        messages.error(request, "Event is full."); return redirect("studentdashboard")
    if event.attendees.filter(pk=request.user.pk).exists():
        messages.info(request, "You already claimed this event."); return redirect("studentdashboard")
    event.attendees.add(request.user)
    messages.success(request, "Ticket claimed."); return redirect("studentdashboard")

@login_required
@csrf_protect
def unclaim_event(request, event_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    if getattr(request.user, "role", None) != 0:
        return JsonResponse({"error": "Student access required"}, status=403)
    event = get_object_or_404(Event, id=event_id)
    if not event.attendees.filter(pk=request.user.pk).exists():
        messages.info(request, "You hadn’t claimed this ticket."); return redirect("studentdashboard")
    event.attendees.remove(request.user)
    messages.success(request, "Ticket unclaimed."); return redirect("studentdashboard")

# -------------------------------
# DRF viewsets (unchanged)
# -------------------------------

class UserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [CanViewUsers]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [perm() for perm in permission_classes]
    def list(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)
    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        return Response(UserSerializer(user).data)
    def create(self, request):
        ser = UserSerializer(data=request.data)
        if ser.is_valid(): ser.save(); return Response(ser.data, status=201)
        return Response(ser.errors, status=400)
    def update(self, request, pk=None):
        try: user = User.objects.get(pk=pk)
        except User.DoesNotExist: return Response({"error":"User not found"}, status=404)
        ser = UserSerializer(user, data=request.data, partial=True)
        if ser.is_valid(): ser.save(); return Response(ser.data)
        return Response(ser.errors, status=400)
    def destroy(self, request, pk=None):
        try: user = User.objects.get(pk=pk); user.delete(); return Response(status=204)
        except User.DoesNotExist: return Response({"error":"User not found"}, status=404)

class EventViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.action in ["list","retrieve"]: permission_classes=[CanViewEvents]
        elif self.action=="create": permission_classes=[CanCreateEvent]
        elif self.action=="update": permission_classes=[CanEditEvent]
        elif self.action=="destroy": permission_classes=[CanDeleteEvent]
        elif self.action in ["register","unregister"]: permission_classes=[CanRegisterEvent]
        else: permission_classes=[permissions.IsAuthenticated]
        return [perm() for perm in permission_classes]
    def list(self, request):
        events = Event.objects.all()
        return Response(EventSerializer(events, many=True).data)
    def retrieve(self, request, pk=None):
        e = Event.objects.filter(pk=pk).first()
        if not e: return Response({"error":"Event not found"}, status=404)
        return Response(EventSerializer(e).data)
    def create(self, request):
        ser = EventCreateSerializer(data=request.data)
        if ser.is_valid():
            e = ser.save(organizer=request.user)
            return Response(EventSerializer(e).data, status=201)
        return Response(ser.errors, status=400)
    def update(self, request, pk=None):
        e = Event.objects.filter(pk=pk).first()
        if not e: return Response({"error":"Event not found"}, status=404)
        ser = EventSerializer(e, data=request.data)
        if ser.is_valid(): ser.save(); return Response(ser.data)
        return Response(ser.errors, status=400)
    def destroy(self, request, pk=None):
        e = Event.objects.filter(pk=pk).first()
        if not e: return Response({"error":"Event not found"}, status=404)
        if e.organizer != request.user and request.user.role != 2:
            return Response({"error":"Not authorized"}, status=403)
        e.delete(); return Response(status=204)
    @action(detail=True, methods=["post"])
    def register(self, request, pk=None):
        e = Event.objects.filter(pk=pk).first()
        if not e: return Response({"error":"Event not found"}, status=404)
        if e.attendees.count() >= e.capacity: return Response({"error":"Event is full"}, status=400)
        if request.user in e.attendees.all(): return Response({"error":"Already registered"}, status=400)
        e.attendees.add(request.user); return Response({"message":"Successfully registered"})
    @action(detail=True, methods=["post"])
    def unregister(self, request, pk=None):
        e = Event.objects.filter(pk=pk).first()
        if not e: return Response({"error":"Event not found"}, status=404)
        if request.user not in e.attendees.all(): return Response({"error":"Not registered"}, status=400)
        e.attendees.remove(request.user); return Response({"message":"Successfully unregistered"})
