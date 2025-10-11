from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.shortcuts import render
from ..models import Event, User
from .serializers import EventSerializer, EventCreateSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from ..forms import StudentSignupForm, OrganizerSignupForm


class UserViewSet(viewsets.ViewSet):
    DUMMY_USERS = [
        {"user_id": 1, "name": "Jana", "email": "jana@example.com", "role": 0, "status": 1},
        {"user_id": 2, "name": "Ali", "email": "ali@example.com", "role": 1, "status": 0},
    ]

    def list(self, request):
        return Response(self.DUMMY_USERS)

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

#EVENT VIEWS

class EventViewSet(viewsets.ViewSet):
    def list(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def create(self, request):
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save(organizer=request.user) 
            return_serializer = EventSerializer(event)
            return Response(return_serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)
        
        serializer = EventSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)
        event.delete()
        return Response(status=204)

    def register(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)
        
        if event.available_spots <= 0:
            return Response(
                {"error": "Event is full"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        event.attendees.add(request.user)
        return Response({"message": "Successfully registered for event"})

    def unregister(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)
        
        event.attendees.remove(request.user)
        return Response({"message": "Successfully unregistered from event"})
    
   
    

# PAGES VIEWS
def loginindex(request):
    return render(request, "loginindex.html")

def signup(request):
    return render(request, "signup.html")

def studentlogin(request):
    return render(request, "studentlogin.html")

def organizerlogin(request):
    return render(request, "organizerlogin.html")

def adminlogin(request):
    return render(request, "adminlogin.html")

def studentdashboard(request):
    return render(request, "studentdashboard.html")

def organizerdashboard(request):
    return render(request, "organizerdashboard.html")

def admindashboard(request):
    return render(request, "admindashboard.html")

def EventList(request):
    return render(request, "EventList.html")

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
            login(request, user)
            request.session['user_role'] = role
            
            if role == 'student':
                return redirect('studentdashboard')
            else:
                return redirect('organizerpending')
        # If form is invalid, it will show errors in the template
    
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