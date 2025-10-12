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

# from django.contrib.auth.models import User

from .forms import OrganizerUpdateForm
from .models import User



@login_required
def update_organizer_profile(request): # ensure only organizers can access
    user = request.user

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('organizer_dashboard')  # or student_dashboard
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'update_organizer_profile.html', {'form': form})

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

def organizer_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)  # username = email

        if user is not None and getattr(user, "role", None) == 1:
            if user.status == 1:  # active
                login(request, user)
                return redirect("organizer_dashboard")
            else:  # pending
                messages.info(request, "Your account is pending admin approval.")
                return render(request, "organizer_pending.html", {"email": email})
        else:
            messages.error(request, "Invalid organizer credentials.")
            return redirect("organizer_login")

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
    # return render(request, 'student_profile.html')
    return render(request, 'studentdashboard.html')

@login_required
def organizer_dashboard(request):
    return render(request, 'organizerdashboard.html')


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
