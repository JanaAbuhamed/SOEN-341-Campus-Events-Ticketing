from rest_framework import viewsets, status, permissions
from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404, render
from ..models import Event, User
from .serializers import EventSerializer, EventCreateSerializer
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from ..forms import StudentSignupForm, OrganizerSignupForm, UserUpdateForm, PasswordUpdateForm
from .permissions import (
    CanViewEvents, CanCreateEvent, CanEditEvent,
    CanDeleteEvent, CanViewUsers
)



class UserViewSet(viewsets.ViewSet):
    """
    DRF-compatible ViewSet for User operations.
    Uses custom permission classes instead of Django decorators.
    """
    permission_classes = [permissions.IsAuthenticated]

    # Optional dummy data for demo/testing
    DUMMY_USERS = [
        {"user_id": 1, "name": "Jana", "email": "jana@example.com", "role": 0, "status": 1},
        {"user_id": 2, "name": "Alib", "email": "ali@example.com", "role": 1, "status": 0},
        {"user_id": 3, "name": "Charlie", "email": "charlie@example.com", "role": 0, "status": 1},
    ]

    def get_permissions(self):
        """
        Dynamically assign permissions based on action.
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [CanViewUsers]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [perm() for perm in permission_classes]

    def list(self, request):
        """List all users (dummy or real)."""
        return Response(self.DUMMY_USERS)

    def retrieve(self, request, pk=None):
        """Get one user by ID."""
        user = next((u for u in self.DUMMY_USERS if u["user_id"] == int(pk)), None)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(user)

    def create(self, request):
        """Create a new dummy user."""
        new_user = request.data.copy()
        new_user["user_id"] = len(self.DUMMY_USERS) + 1
        self.DUMMY_USERS.append(new_user)
        return Response(new_user, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Update dummy user data."""
        user = next((u for u in self.DUMMY_USERS if u["user_id"] == int(pk)), None)
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        for key, value in request.data.items():
            user[key] = value
        return Response(user)

    def destroy(self, request, pk=None):
        """Delete a user (called via DELETE /api/users/<pk>/)"""
        # Find the user in the class-level DUMMY_USERS
        user = next((u for u in UserViewSet.DUMMY_USERS if u["user_id"] == int(pk)), None)
        if not user:
            return Response({"error": "User not found"}, status=404)

        # Remove the user from the class variable
        UserViewSet.DUMMY_USERS = [u for u in UserViewSet.DUMMY_USERS if u["user_id"] != int(pk)]

        # Return HTTP 204 (No Content) to indicate deletion
        return Response(status=204)


#EVENT VIEWS

class EventViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [CanViewEvents]
        elif self.action == 'create':
            permission_classes = [CanCreateEvent]
        elif self.action == 'update':
            permission_classes = [CanEditEvent]
        elif self.action == 'destroy':
            permission_classes = [CanDeleteEvent]
        elif self.action in ['register', 'unregister']:
            permission_classes = [CanRegisterEvent]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [perm() for perm in permission_classes]

    def list(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        event = Event.objects.filter(pk=pk).first()
        if not event:
            return Response({"error": "Event not found"}, status=404)
        return Response(EventSerializer(event).data)

    def create(self, request):
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save(organizer=request.user)
            return Response(EventSerializer(event).data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        event = Event.objects.filter(pk=pk).first()
        if not event:
            return Response({"error": "Event not found"}, status=404)
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        event = Event.objects.filter(pk=pk).first()
        if not event:
            return Response({"error": "Event not found"}, status=404)
        if event.organizer != request.user and request.user.role != 2:
            return Response({"error": "Not authorized"}, status=403)
        event.delete()
        return Response(status=204)

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = Event.objects.filter(pk=pk).first()
        if not event:
            return Response({"error": "Event not found"}, status=404)
        if event.available_spots <= 0:
            return Response({"error": "Event is full"}, status=400)
        if request.user in event.attendees.all():
            return Response({"error": "Already registered"}, status=400)
        event.attendees.add(request.user)
        event.available_spots -= 1
        event.save()
        return Response({"message": "Successfully registered"})

    @action(detail=True, methods=['post'])
    def unregister(self, request, pk=None):
        event = Event.objects.filter(pk=pk).first()
        if not event:
            return Response({"error": "Event not found"}, status=404)
        if request.user not in event.attendees.all():
            return Response({"error": "Not registered"}, status=400)
        event.attendees.remove(request.user)
        event.available_spots += 1
        event.save()
        return Response({"message": "Successfully unregistered"})
    
   
    

# PAGES VIEWS
def loginindex(request):
    return render(request, "loginindex.html")

def organizerlogin(request):
    return render(request, "organizerlogin.html")

def adminlogin(request):
    return render(request, "adminlogin.html")

@login_required
#@permission_required('main.can_view_events', raise_exception=True)
def studentdashboard(request):
    
    if request.user.role != 0:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Student access required")
    
    # Add debug print to confirm it's working
    print(f"SUCCESS: Student dashboard accessed by {request.user.email}")
    
    return render(request, "studentdashboard.html")


def organizerdashboard(request):
    return render(request, "organizerdashboard.html")

def admindashboard(request):
    return render(request, "admindashboard.html")


def organizerpending(request):
    return render(request, "organizer-pending.html")


#FUNCTION-BASED VIEWS

def signup(request):
    if request.method == "POST":
        role = request.POST.get('role')
        
        if role == 'student':
            form = StudentSignupForm(request.POST)
        else:
            form = OrganizerSignupForm(request.POST)
            
        if form.is_valid():
            user = form.save()
            
            if role == 'student':
                group = Group.objects.get(name='Student')
                user.groups.add(group)
            else:
                group = Group.objects.get(name='Organizer') 
                user.groups.add(group)
            
            login(request, user)
            request.session['user_role'] = role
            
            if role == 'student':
                return redirect('studentdashboard')
            else:
                return redirect('organizerpending')
    else:
        form = StudentSignupForm()
    
    return render(request, "signup.html", {'form': form})

def studentlogin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None and user.role == 0:  # Check if user is a student
            login(request, user)
            return redirect('studentdashboard')
        else:
            return render(request, "studentlogin.html", {'error': 'Invalid credentials or not a student account'})
    
    return render(request, "studentlogin.html")

def organizerlogin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None and user.role == 1:  # Check if user is an organizer
            if user.status == 1:  # Check if organizer is approved
                login(request, user)
                return redirect('organizerdashboard')
            else:
                return render(request, "organizerlogin.html", {'error': 'Organizer account pending approval'})
        else:
            return render(request, "organizerpending.html")
    
    return render(request, "organizerlogin.html")


def adminlogin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None and user.role == 2:
            login(request, user)
            return redirect('admindashboard')
        else:
            return render(request, "adminlogin.html", {'error': 'Admin accounts only'})
    
    return render(request, "adminlogin.html")

# RBAC PROTECTED VIEWS
# Student Views


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

@login_required
@permission_required('main.can_register_event', raise_exception=True)
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if event.available_spots <= 0:
        return JsonResponse({'error': 'Event is full'}, status=400)
    
    if request.user in event.attendees.all():
        return JsonResponse({'error': 'Already registered'}, status=400)
    
    event.attendees.add(request.user)
    event.available_spots -= 1
    event.save()
    
    return JsonResponse({'message': 'Successfully registered for event'})

@login_required
@permission_required('main.can_register_event', raise_exception=True)
def unregister_from_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.user not in event.attendees.all():
        return JsonResponse({'error': 'Not registered for this event'}, status=400)
    
    event.attendees.remove(request.user)
    event.available_spots += 1
    event.save()
    
    return JsonResponse({'message': 'Successfully unregistered from event'})







# Organizer Views
@login_required
@permission_required('main.can_create_event', raise_exception=True)
def create_event(request):
    if request.method == "POST":
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save(organizer=request.user)
            return JsonResponse({'message': 'Event created successfully', 'event_id': event.id})
        return JsonResponse(serializer.errors, status=400)
    return render(request, "create_event.html")

@login_required
@permission_required('main.can_edit_event', raise_exception=True)
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    if request.method == "POST":
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'Event updated successfully'})
        return JsonResponse(serializer.errors, status=400)
    
    return render(request, "edit_event.html", {'event': event})

@login_required
@permission_required('main.can_delete_event', raise_exception=True)
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    
    if request.method == "POST":
        event.delete()
        return JsonResponse({'message': 'Event deleted successfully'})
    
    return render(request, "delete_event.html", {'event': event})

# Admin Views
@login_required
@permission_required('main.can_approve_organizer', raise_exception=True)
def admin_approve_organizers(request):
    if request.user.role != 2:  # Additional admin role check
        return HttpResponseForbidden("Admin access required")
    
    pending_organizers = User.objects.filter(role=1, status=0)
    
    if request.method == "POST":
        organizer_id = request.POST.get('organizer_id')
        action = request.POST.get('action')
        
        organizer = get_object_or_404(User, id=organizer_id, role=1, status=0)
        
        if action == 'approve':
            organizer.status = 1
            organizer.save()
            return JsonResponse({'message': 'Organizer approved successfully'})
        elif action == 'reject':
            organizer.delete()
            return JsonResponse({'message': 'Organizer application rejected'})
    
    return render(request, "admin_approve.html", {'pending_organizers': pending_organizers})

@login_required
@permission_required('main.can_approve_organizer', raise_exception=True)
def admin_dashboard(request):
    if request.user.role != 2:
        return HttpResponseForbidden("Admin access required")
    
    stats = {
        'total_events': Event.objects.count(),
        'total_students': User.objects.filter(role=0).count(),
        'total_organizers': User.objects.filter(role=1).count(),
        'pending_approvals': User.objects.filter(role=1, status=0).count(),
    }
    
    return render(request, "admindashboard.html", {'stats': stats})