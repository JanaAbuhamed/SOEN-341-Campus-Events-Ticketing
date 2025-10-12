# main/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import PasswordUpdateForm

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import authenticate, login

from django.contrib.auth.models import User

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
    # return render(request, 'student_profile.html')
    return render(request, 'studentdashboard.html')



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