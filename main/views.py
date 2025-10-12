from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, User
from .forms import EventForm

def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    form = EventForm(request.POST or None, instance=event)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('organizer-dashboard')

    return render(request, 'edit_event.html', {'form': form, 'event': event})

def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('organizer-dashboard')

def organizer_dashboard(request):
    # Simulate organizer login for testing (replace with request.user when login is ready)
    organizer = User.objects.get(email="org1@mail.com")

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        time = request.POST.get('time')
        location = request.POST.get('location')
        capacity = request.POST.get('capacity')

        Event.objects.create(
            title=title,
            description=description,
            date=date,
            time=time,
            location=location,
            capacity=capacity,
            organizer=organizer,
            status='pending'  # Event starts in pending state
        )
        return redirect('organizer-dashboard')

    # Split events by status for dashboard display
    approved_events = Event.objects.filter(organizer=organizer, status='approved')
    pending_events = Event.objects.filter(organizer=organizer, status='pending')
    rejected_events = Event.objects.filter(organizer=organizer, status='rejected')

    return render(request, 'organizerdashboard.html', {
        'approved_events': approved_events,
        'pending_events': pending_events,
        'rejected_events': rejected_events
    })