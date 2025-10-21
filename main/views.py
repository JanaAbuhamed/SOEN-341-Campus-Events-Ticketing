# main/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import EventForm, OrganizerUpdateForm
from .models import User, Event


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
    Organizer dashboard:
    - Only role=1 allowed.
    - Create events (saved as 'pending' for admin approval).
    - List organizer's approved/pending/rejected events.
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
            event.status = "pending"  # admin approval required
            event.save()
            messages.success(request, "Event submitted for admin approval.")
            return redirect("organizerdashboard")
        else:
            messages.error(request, "Please fix the errors in the form.")
    else:
        form = EventForm()

    approved_events = Event.objects.filter(organizer=organizer, status="approved")
    pending_events = Event.objects.filter(organizer=organizer, status="pending")
    rejected_events = Event.objects.filter(organizer=organizer, status="rejected")

    return render(
        request,
        "organizerdashboard.html",
        {
            "form": form,
            "approved_events": approved_events,
            "pending_events": pending_events,
            "rejected_events": rejected_events,
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
