from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action

from django.http import HttpResponseForbidden, JsonResponse

from ..models import Event, User, Ticket
from .serializers import EventSerializer, EventCreateSerializer, TicketSerializer
from ..forms import StudentSignupForm, OrganizerSignupForm, UserUpdateForm, PasswordUpdateForm


# ---------------------------
# Users (dummy viewset you had)
# ---------------------------
class UserViewSet(viewsets.ViewSet):
    DUMMY_USERS = [
        {"user_id": 1, "name": "Jana", "email": "jana@example.com", "role": 0, "status": 1},
        {"user_id": 2, "name": "Ali", "email": "ali@example.com", "role": 1, "status": 0},
    ]

    @permission_required('main.can_view_events', raise_exception=True)
    def list(self, request):
        return Response(self.DUMMY_USERS)

    @permission_required('main.can_view_events', raise_exception=True)
    def retrieve(self, request, pk=None):
        user = next((u for u in self.DUMMY_USERS if u["user_id"] == int(pk)), None)
        if not user:
            return Response({"error": "User not found"}, status=404)
        return Response(user)

    def create(self, request):
        new_user = request.data
        new_user["user_id"] = len(self.DUMMY_USERS) + 1
        self.DUMMY_USERS.append(new_user)
        return Response(new_user, status=201)

    def update(self, request, pk=None):
        user = next((u for u in self.DUMMY_USERS if u["user_id"] == int(pk)), None)
        if not user:
            return Response({"error": "User not found"}, status=404)
        for key, value in request.data.items():
            user[key] = value
        return Response(user)

    def destroy(self, request, pk=None):
        user = next((u for u in self.DUMMY_USERS if u["user_id"] == int(pk)), None)
        if not user:
            return Response({"error": "User not found"}, status=404)
        self.DUMMY_USERS = [u for u in self.DUMMY_USERS if u["user_id"] != int(pk)]
        return Response(status=204)


# ---------------------------
# Events + registration
# ---------------------------
class EventViewSet(viewsets.ViewSet):
    @permission_required('main.can_view_events', raise_exception=True)
    def list(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    @permission_required('main.can_view_events', raise_exception=True)
    def retrieve(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    @permission_required('main.can_create_event', raise_exception=True)
    def create(self, request):
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save(organizer=request.user)
            return_serializer = EventSerializer(event)
            return Response(return_serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @permission_required('main.can_edit_event', raise_exception=True)
    def update(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @permission_required('main.can_delete_event', raise_exception=True)
    def destroy(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        if event.organizer != request.user and request.user.role != 2:
            return Response({"error": "Not authorized to delete this event"}, status=403)
        event.delete()
        return Response(status=204)

    @permission_required('main.can_register_event', raise_exception=True)
    def register(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)

        if event.available_spots() <= 0:
            return Response({"error": "Event is full"}, status=status.HTTP_400_BAD_REQUEST)

        if request.user in event.attendees.all():
            # already registered — return existing ticket
            ticket = Ticket.objects.get(user=request.user, event=event)
            data = TicketSerializer(ticket, context={"request": request}).data
            return Response({"message": "Already registered", "ticket": data}, status=200)

        # register + generate ticket
        event.attendees.add(request.user)
        ticket, _ = Ticket.objects.get_or_create(user=request.user, event=event)
        data = TicketSerializer(ticket, context={"request": request}).data
        return Response({"message": "Successfully registered", "ticket": data}, status=201)

    @permission_required('main.can_register_event', raise_exception=True)
    def unregister(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        if request.user not in event.attendees.all():
            return Response({"error": "Not registered for this event"}, status=400)

        event.attendees.remove(request.user)
        Ticket.objects.filter(user=request.user, event=event).delete()
        return Response({"message": "Successfully unregistered from event"})


# ---------------------------
# Tickets API
# ---------------------------
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def my_tickets(request):
    qs = Ticket.objects.filter(user=request.user).select_related("event")
    data = TicketSerializer(qs, many=True, context={"request": request}).data
    return Response(data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])  # scanning device may not be authenticated
def verify_ticket(request, code: str):
    try:
        ticket = Ticket.objects.select_related("event", "user").get(code=code)
        return Response({
            "valid": True,
            "code": ticket.code,
            "event": ticket.event.title,
            "when": ticket.event.date,
            "who": ticket.user.email,
        })
    except Ticket.DoesNotExist:
        return Response({"valid": False, "error": "Invalid ticket"}, status=404)


# ---------------------------
# Your existing page views (left as-is)
# ---------------------------
def loginindex(request): return render(request, "loginindex.html")
def organizerlogin(request): return render(request, "organizerlogin.html")
def adminlogin(request): return render(request, "adminlogin.html")

@login_required
def studentdashboard(request):
    if request.user.role != 0:
        return HttpResponseForbidden("Student access required")
    print(f"SUCCESS: Student dashboard accessed by {request.user.email}")
    return render(request, "studentdashboard.html")

def organizerdashboard(request): return render(request, "organizerdashboard.html")
def admindashboard(request): return render(request, "admindashboard.html")
def organizerpending(request): return render(request, "organizer-pending.html")

def signup(request):
    if request.method == "POST":
        role = request.POST.get('role')
        form = StudentSignupForm(request.POST) if role == 'student' else OrganizerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                group = Group.objects.get(name='Student' if role=='student' else 'Organizer')
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
            login(request, user)
            request.session['user_role'] = role
            return redirect('studentdashboard' if role == 'student' else 'organizerpending')
    else:
        form = StudentSignupForm()
    return render(request, "signup.html", {'form': form})

def studentlogin(request):
    if request.method == "POST":
        email = request.POST.get('email'); password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.role == 0:
            login(request, user); return redirect('studentdashboard')
        return render(request, "studentlogin.html", {'error': 'Invalid credentials or not a student account'})
    return render(request, "studentlogin.html")

def organizerlogin(request):
    if request.method == "POST":
        email = request.POST.get('email'); password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.role == 1:
            if user.status == 1:
                login(request, user); return redirect('organizerdashboard')
            return render(request, "organizerlogin.html", {'error': 'Organizer account pending approval'})
        return render(request, "organizerpending.html")
    return render(request, "organizerlogin.html")

def adminlogin(request):
    if request.method == "POST":
        email = request.POST.get('email'); password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.role == 2:
            login(request, user); return redirect('admindashboard')
        return render(request, "adminlogin.html", {'error': 'Admin accounts only'})
    return render(request, "adminlogin.html")

@login_required
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('studentdashboard')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'update_profile.html', {'form': form})

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
    else:
        form = PasswordUpdateForm(request.user)
    return render(request, "update_password.html", {"form": form})

@login_required
@permission_required('main.can_view_events', raise_exception=True)
def EventList(request):
    events = Event.objects.all()
    return render(request, "EventList.html", {'events': events})
