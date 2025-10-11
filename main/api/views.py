from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from ..models import Event, User
from .serializers import EventSerializer, EventCreateSerializer


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
    
