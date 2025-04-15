from django import forms
from django.contrib.auth.models import User
from .models import Profile

# Form for updating user details (name, email)
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

# Form for updating profile details (phone, address, and profile picture)
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'phone', 'address']
# forms.py

