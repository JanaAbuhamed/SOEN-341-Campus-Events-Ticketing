# main/views.py
from django.contrib import messages
from django.db import models 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncDate
import csv

from .forms import EventForm, OrganizerUpdateForm
from .models import User, Event, SavedEvent, Payment

from rest_framework import viewsets
# from main.models import User, Event
from main.serializers import UserSerializer, EventSerializer
from rest_framework.permissions import IsAuthenticated

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [...]  # optional

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]  # restrict create to logged-in users



@login_required
def update_organizer_profile(request):
    """
    Allow an approved Organizer (role=1, status=1) to update their profile.
    """
    if getattr(request.user, "role", None) != 1:
        messages.error(request, "Access denied: organizers only.")
        return redirect("organizerlogin")

    organizer = request.user

    if request.method == "POST":
        form = OrganizerUpdateForm(request.POST, instance=organizer)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("organizerdashboard")
    else:
        form = OrganizerUpdateForm(instance=organizer)

    return render(request, "update_organizer_profile.html", {"form": form})

@login_required
def organizer_dashboard(request):
    """
    Organizer dashboard with sorting functionality
    """
    if getattr(request.user, "role", None) != 1:
        messages.error(request, "Access denied: organizers only.")
        return redirect("organizerlogin")

    organizer = request.user

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = organizer
            event.status = "pending"
            event.save()
            messages.success(request, "Event submitted for admin approval.")
            return redirect("organizerdashboard")
        else:
            messages.error(request, "Please fix the errors in the form.")
    else:
        form = EventForm()

    # Get sorting parameter
    sort_by = request.GET.get('sort', 'created_at')  # default sort by created date
    
    # Base querysets
    approved_events = Event.objects.filter(organizer=organizer, status="approved")
    pending_events = Event.objects.filter(organizer=organizer, status="pending")
    rejected_events = Event.objects.filter(organizer=organizer, status="rejected")
    
    # Apply sorting to approved events
    if sort_by == 'event_date':
        approved_events = approved_events.order_by('date')
    elif sort_by == 'tickets_issued':
        # Annotate with attendee count for sorting
        approved_events = approved_events.annotate(
            attendee_count=models.Count('attendees')
        ).order_by('-attendee_count')
    else:  # published_date (created_at)
        approved_events = approved_events.order_by('-created_at')

    return render(
        request,
        "organizerdashboard.html",
        {
            "form": form,
            "approved_events": approved_events,
            "pending_events": pending_events,
            "rejected_events": rejected_events,
            "current_sort": sort_by,
        },
    )

@login_required
def organizer_analytics(request):
    if getattr(request.user, "role", None) != 1:
        messages.error(request, "Access denied: organizers only.")
        return redirect("organizerlogin")

    organizer = request.user
    
    # Get all events for this organizer
    all_events = Event.objects.filter(organizer=organizer)
    
    # Calculate overall statistics
    total_events = all_events.count()
    approved_events = all_events.filter(status='approved')
    pending_events = all_events.filter(status='pending')
    rejected_events = all_events.filter(status='rejected')
    
    # Calculate attendance statistics
    total_attendees = sum(event.attendees.count() for event in approved_events)
    total_capacity = sum(event.capacity for event in approved_events)
    overall_attendance_rate = (total_attendees / total_capacity * 100) if total_capacity > 0 else 0
    
    # Calculate saved events statistics
    total_saves = SavedEvent.objects.filter(event__organizer=organizer).count()
    
    # Per-event analytics for approved events
    event_analytics = []
    for event in approved_events:
        attendees_count = event.attendees.count()
        attendance_rate = (attendees_count / event.capacity * 100) if event.capacity > 0 else 0
        saves_count = event.saved_by.count()  # Using the related_name from SavedEvent
        
        # Engagement metrics
        save_to_attendance_ratio = (saves_count / attendees_count * 100) if attendees_count > 0 else 0
        engagement_score = (attendees_count + saves_count) / event.capacity * 100 if event.capacity > 0 else 0
        
        event_analytics.append({
            'event': event,
            'attendees_count': attendees_count,
            'attendance_rate': round(attendance_rate, 1),
            'available_spots': event.available_spots(),
            'saves_count': saves_count,
            'save_to_attendance_ratio': round(save_to_attendance_ratio, 1),
            'engagement_score': round(engagement_score, 1),
        })
    
    # Sort events by engagement score (most engaging first)
    event_analytics.sort(key=lambda x: x['engagement_score'], reverse=True)
    
    analytics_data = {
        'total_events': total_events,
        'approved_count': approved_events.count(),
        'pending_count': pending_events.count(),
        'rejected_count': rejected_events.count(),
        'total_attendees': total_attendees,
        'total_capacity': total_capacity,
        'overall_attendance_rate': round(overall_attendance_rate, 1),
        'total_saves': total_saves,
        'event_analytics': event_analytics,
    }

    return render(
        request,
        "organizeranalytics.html",
        {
            "analytics": analytics_data,
        },
    )

@login_required
def edit_event(request, event_id):
    """
    Edit an event owned by the current organizer.
    """
    if getattr(request.user, "role", None) != 1:
        messages.error(request, "Access denied: organizers only.")
        return redirect("organizerlogin")

    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    form = EventForm(request.POST or None, instance=event)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Event updated.")
        return redirect("organizerdashboard")

    return render(request, "edit_event.html", {"form": form, "event": event})


@login_required
def delete_event(request, event_id):
    """
    Delete an event owned by the current organizer.
    """
    if getattr(request.user, "role", None) != 1:
        messages.error(request, "Access denied: organizers only.")
        return redirect("organizerlogin")

    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    event.delete()
    messages.success(request, "Event deleted.")
    return redirect("organizerdashboard")


@login_required
def export_attendees_csv(request, event_id):
    """
    Allow organizers to export attendee data for their event as a CSV file.
    """
    if getattr(request.user, "role", None) != 1:
        messages.error(request, "Access denied: organizers only.")
        return redirect("organizerlogin")

    # Ensure event belongs to this organizer
    event = get_object_or_404(Event, id=event_id, organizer=request.user)

    # Create CSV response
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{event.title}_attendees.csv"'

    writer = csv.writer(response)
    writer.writerow(["Full Name", "Email", "Purchase Date"])

    # Loop through Ticket objects instead of just attendees
    tickets = event.ticket_set.all()  # all Ticket objects related to this event
    for ticket in tickets:
        writer.writerow([ticket.user.name, ticket.user.email, ticket.purchase_date.strftime("%Y-%m-%d %H:%M")])

    return response

@login_required
def participation_trend(request):
    data = (
        SavedEvent.objects
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )
    return JsonResponse(list(data), safe=False)

@login_required
def claim_trend_by_payment(request):
    # Aggregate payments per day
    qs = (
        Payment.objects
        .annotate(date=TruncDate('created_at'))  # or 'timestamp' field
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    data = [{"date": str(entry["date"]), "count": entry["count"]} for entry in qs]
    return JsonResponse(data, safe=False)