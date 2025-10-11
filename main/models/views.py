# student/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm

@login_required
def update_profile(request):
    user = request.user  # currently logged-in user

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('student_dashboard')  # your dashboard URL name. reload page after save
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'studentdashboard.html', {'form': form})


