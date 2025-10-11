from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class BaseUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Name',
        'class': 'form-input'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Email address', 
        'class': 'form-input'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password',
        'class': 'form-input'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        'class': 'form-input'
    }))

    class Meta:
        model = User
        fields = ('name', 'email', 'password1', 'password2')

class StudentSignupForm(BaseUserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']
        user.role = 0  # Student
        user.status = 1  # Active immediately
        
        if commit:
            user.save()
        return user

class OrganizerSignupForm(BaseUserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']
        user.role = 1  # Organizer
        user.status = 0  # Pending approval
        
        if commit:
            user.save()
        return user