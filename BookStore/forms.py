from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser  # Import the custom user model

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'profile_pic', 'phone', 'address']
