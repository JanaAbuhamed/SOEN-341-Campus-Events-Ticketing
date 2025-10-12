from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Event, User
from .serializers import EventSerializer, EventCreateSerializer


# ---------- USER (dummy) ----------
class UserViewSet(viewsets.ViewSet):
    """
    Simple in-memory users just to exercise the endpoints.
    """
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
        new_user = dict(request.data)
        new_user["user_id"] = len(self.DUMMY_USERS) + 1
        self.DUMMY_USERS.append(new_user)
        return Response(new_user, status=201)

    def update(self, request, pk=None):
        user = next((u for u in self.DUMMY_USERS if u["user_id"] == int(pk)), None)
        if not user:
            return Response({"error": "User not found"}, status=404)
        for k, v in request.data.items():
            user[k] = v
        return Response(user)

    def destroy(self, request, pk=None):
        user = next((u for u in self.DUMMY_USERS if u["user_id"] == int(pk)), None)
        if not user:
            return Response({"error": "User not found"}, status=404)
        self.DUMMY_USERS = [u for u in self.DUMMY_USERS if u["user_id"] != int(pk)]
        return Response(status=204)


# ---------- EVENT ----------
class EventViewSet(viewsets.ViewSet):
    """
    CRUD + register / unregister for Event.
    """

    def list(self, request):
        events = Event.objects.all()
        return Response(EventSerializer(events, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)
        return Response(EventSerializer(event).data)

    def create(self, request):
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Organizer is whoever is logged in
            organizer = request.user if request.user and request.user.is_authenticated else None
            event = serializer.save(organizer=organizer)
            return Response(EventSerializer(event).data, status=201)
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

    @action(detail=True, methods=["post"])
    def register(self, request, pk=None):
        """
        Add the current user to the event's attendees if there is capacity.
        """
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)

        # Determine available spots regardless of whether it's a field, @property, or method.
        spots_attr = getattr(event, "available_spots", None)
        spots = spots_attr() if callable(spots_attr) else spots_attr

        if spots is not None and spots <= 0:
            return Response({"error": "Event is full"}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user or not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        event.attendees.add(request.user)
        return Response({"message": "Successfully registered for event"})

    @action(detail=True, methods=["post"])
    def unregister(self, request, pk=None):
        """
        Remove the current user from the event's attendees.
        """
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)

        if not request.user or not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        event.attendees.remove(request.user)
        return Response({"message": "Successfully unregistered from event"})


# ---------- CLAIMED TICKETS (FullCalendar feed) ----------
class MyClaimedTicketsView(APIView):
    """
    Returns events where the user is in Event.attendees as FullCalendar items.
    For quick testing we accept ?email=... (defaults to your admin).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.GET.get("email", "admin@gmail.com")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response([], status=200)

        qs = Event.objects.filter(attendees=user).only("id", "title", "date", "time")
        events = [
            {"id": e.id, "title": e.title, "start": f"{e.date}T{(e.time or '00:00:00')}"}
            for e in qs
        ]
        return Response(events, status=200)
