# main/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, EventForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import PasswordUpdateForm

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import authenticate, login

from main.models import User, Event

# from django.contrib.auth.models import User

from .forms import OrganizerUpdateForm
from .models import User, Event
from django.http import JsonResponse





# @login_required
# def update_organizer_profile(request): # ensure only organizers can access
#     user = request.user

#     if request.method == 'POST':
#         form = UserUpdateForm(request.POST, instance=user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Your profile has been updated successfully!")
#             return redirect('organizer_dashboard')  # or student_dashboard
#     else:
#         form = UserUpdateForm(instance=user)

#     return render(request, 'update_organizer_profile.html', {'form': form})


@login_required
def update_organizer_profile(request):
    if request.user.role != 1:
        messages.error(request, "Access denied: organizers only.")
        return redirect('organizerlogin')

    organizer = request.user

    if request.method == 'POST':
        form = OrganizerUpdateForm(request.POST, instance=organizer)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('organizerdashboard')
    else:
        form = OrganizerUpdateForm(instance=organizer)

    return render(request, 'update_organizer_profile.html', {'form': form})





@login_required(login_url='organizerlogin')
def organizer_dashboard(request):
    user = request.user

    # Only organizers can access
    if user.role != 1:
        messages.error(request, "Access denied: organizers only.")
        return redirect("loginindex")

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = user
            event.status = 'pending'  # pending approval
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('organizerdashboard')
        else:
            messages.error(request, "Error creating event. Please check form.")
    else:
        form = EventForm()

    approved_events = Event.objects.filter(organizer=user, status='approved')
    pending_events = Event.objects.filter(organizer=user, status='pending')
    rejected_events = Event.objects.filter(organizer=user, status='rejected')

    return render(request, 'organizerdashboard.html', {
        'form': form,
        'approved_events': approved_events,
        'pending_events': pending_events,
        'rejected_events': rejected_events
    })






def organizer_signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("organizer_signup")

        # role 1 = Organizer, status 0 = Pending approval
        user = User.objects.create_user(
            email=email,
            username=email,  # keep username = email
            name=name,
            password=password,
            role=1,
            status=0  # pending approval
        )
        user.save()

        messages.success(request, "Organizer account created! Waiting for admin approval.")
        return redirect("organizer_login")

    return render(request, "organizer_signup.html")

# def organizer_login(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         password = request.POST.get("password")

#         user = authenticate(request, username=email, password=password)

#         if user is not None and user.role == 1:
#             if user.status == 1:
#                 login(request, user)
#                 return redirect("organizerdashboard")
#             else:
#                 messages.info(request, "Your account is pending admin approval.")
#                 return render(request, "organizer-pending.html", {"email": email})
#         else:
#             messages.error(request, "Invalid organizer credentials.")
#             return redirect("organizerlogin")
#     return render(request, "organizerlogin.html")



def organizer_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None and user.role == 1:
            if user.status == 1:  # Approved organizer
                login(request, user)
                return redirect("organizerdashboard")
            else:
                return render(request, "organizer-pending.html", {"email": user.email})
        else:
            messages.error(request, "Invalid organizer credentials.")
            return redirect("organizerlogin")
    return render(request, "organizerlogin.html")







def signup_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('signup')

        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        user.save()
        messages.success(request, f'{user_type.capitalize()} account created successfully! You can now log in.')
        return redirect('student_login')

    return render(request, 'signup.html')


def student_signup(request):
    return render(request, 'signup.html')

def student_login(request):
    if request.method == "POST":
        email = request.POST.get("username")  # form field is "username" in HTML
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("student_dashboard")  # change this if dashboard view name is different
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("student_login")
    return render(request, "studentlogin.html")


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


@login_required
def student_profile(request):
    user = request.user
    return render(request, 'student_profile.html', {'user': user})


@login_required
def student_dashboard(request):
    user = request.user

    # Show only events this student registered for
    registered_events = Event.objects.filter(attendees=user)

    event_data = [
        {
            "title": e.title,
            "date": str(e.date),
            "time": str(e.time),
            "location": e.location,
            "ticket_type": e.ticket_type,
            "capacity": e.capacity,
            "organizer": e.organizer.name,
        }
        for e in registered_events
    ]

    return render(request, "studentdashboard.html", {'events': event_data})


    event_data = [
        {"title": e.title, "date": str(e.date), "time": str(e.time), "location": e.location}
        for e in events
    ]
    return render(request, 'studentdashboard.html', {'events': event_data})

@login_required
# def organizer_dashboard(request):
#     return render(request, 'organizerdashboard.html')
# @login_required
# def organizer_dashboard(request):
#     user = request.user

#     # Only organizers can access
#     if user.role != 1:
#         messages.error(request, "Access denied: organizers only.")
#         return redirect("loginindex")

#     # Handle creating new events
#     if request.method == 'POST':
#         form = EventForm(request.POST)
#         if form.is_valid():
#             event = form.save(commit=False)
#             event.organizer = user
#             event.status = 'pending'
#             event.save()
#             messages.success(request, "Event created successfully!")
#             return redirect('organizerdashboard')
#         else:
#             print("❌ Form errors:", form.errors)
#     else:
#         form = EventForm()

    # approved_events = Event.objects.filter(organizer=user, status='approved')
    # pending_events = Event.objects.filter(organizer=user, status='pending')
    # rejected_events = Event.objects.filter(organizer=user, status='rejected')

    # return render(request, 'organizerdashboard.html', {
    #     'form': form,
    #     'approved_events': approved_events,
    #     'pending_events': pending_events,
    #     'rejected_events': rejected_events
    # })

# Organizer dashboard view
def organizer_dashboard(request):
    if request.user.role != 1:
        return redirect('some-appropriate-page')  # only organizers allowed

    organizer = request.user  # logged-in user
    events = organizer.organized_events.all()  # get their events
    return render(request, 'organizerdashboard.html', {'organizer': organizer, 'events': events})



# for student
@login_required
def update_profile(request):
    user = request.user  # currently logged-in user

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('student_dashboard')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'update_profile.html', {'form': form})



# for student
@login_required 
def update_password(request):
    if request.method == "POST":
        form = PasswordUpdateForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # keeps user logged in
            messages.success(request, "Your password has been updated successfully!")
            return redirect("student_dashboard")
    else:
        form = PasswordUpdateForm(request.user)
    return render(request, "update_password.html", {"form": form})

from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, User
from .forms import EventForm

def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    form = EventForm(request.POST or None, instance=event)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('organizerdashboard')

    return render(request, 'edit_event.html', {'form': form, 'event': event})

def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('organizerdashboard')


@login_required(login_url='studentlogin')
def eventlist(request):
    events = Event.objects.filter(status='approved')
    return render(request, 'eventlist.html', {'events': events})

from django.http import JsonResponse

def eventlist_api(request):
    """Return approved events as JSON."""
    events = list(Event.objects.filter(status='approved').values(
        'id', 'title', 'description', 'date', 'time', 'location',
        'capacity', 'ticket_type', 'status',
        'organizer__name'
    ))
    return JsonResponse(events, safe=False)

@login_required(login_url='studentlogin')
def student_calendar(request):
    """Display a calendar of the student's registered or available events."""
    user = request.user

    # For now: show all approved events
    events = Event.objects.filter(status='approved')

    event_data = [
        {
            "title": e.title,
            "start": f"{e.date}T{e.time}",
            "location": e.location,
        }
        for e in events
    ]

    return render(request, "studentcalendar.html", {"events": event_data})

from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='studentlogin')
@csrf_exempt
def register_event(request, event_id):
    """Registers the current student for a specific event."""
    if request.method == "POST":
        try:
            event = Event.objects.get(id=event_id)

            # Check if already registered
            if request.user in event.attendees.all():
                return JsonResponse({"message": "Already registered for this event."}, status=400)

            # Register student
            event.attendees.add(request.user)
            event.save()

            return JsonResponse({"message": f"Successfully registered for {event.title}!"}, status=200)
        except Event.DoesNotExist:
            return JsonResponse({"message": "Event not found."}, status=404)
        except Exception as e:
            print("❌ Register error:", e)
            return JsonResponse({"message": "Error registering for event"}, status=400)
    return JsonResponse({"message": "Invalid request"}, status=405)

@login_required(login_url='studentlogin')
@csrf_exempt
def unregister_event(request, event_id):
    """Unregisters the current student from a specific event."""
    if request.method == "POST":
        try:
            event = Event.objects.get(id=event_id)
            return JsonResponse({"message": f"Unregistered from {event.title}."}, status=200)
        except Event.DoesNotExist:
            return JsonResponse({"message": "Event not found."}, status=404)
        except Exception as e:
            print("❌ Unregister error:", e)
            return JsonResponse({"message": "Error unregistering from event"}, status=400)
    return JsonResponse({"message": "Invalid request"}, status=405)
