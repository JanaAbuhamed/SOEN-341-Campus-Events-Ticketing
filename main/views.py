# main/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import PasswordUpdateForm


@login_required
def student_dashboard(request):
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
