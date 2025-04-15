from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
import requests
import random
from django.contrib.auth.hashers import make_password
from django.conf import settings
from .models import Profile
from .forms import ProfileUpdateForm, UserUpdateForm 
 
from .utils import check_password_strength  # Assuming you have utils.py with this function

User = get_user_model()  # Use the custom user model

# Password Strength Check View
def check_password_view(request):
    password_strength = None
    password_valid = False

    if request.method == 'POST':
        password = request.POST.get('password1')
        password_valid, password_strength = check_password_strength(password)

    return render(request, 'register.html', {
        'password_strength': password_strength,
        'password_valid': password_valid,
    })

# Function to validate name (username)
def verif_nom(nom):
    return len(nom) > 3 and nom.isalpha()

# Register User View
def register_user(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        

        if not verif_nom(username) or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
        elif password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                
            )
            user.save()

            user = authenticate(username=username, password=password1)
            if user:
                login(request, user)
                messages.success(request, "You have successfully registered! Welcome!")
                return redirect('home')
            else:
                messages.error(request, "Registration failed. Please try again.")

    return render(request, 'register.html')

# User Login View
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in! Welcome!")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, 'login.html')

# Home View
def home(request):
    return render(request, 'home.html')

# User Logout View
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('login')

# External API Call
def use_api(request):
    url1 = "https://openlibrary.org/api/books?bibkeys=ISBN:0451526538&format=json&jscmd=data"
    url2 = "https://openlibrary.org/api/books?bibkeys=ISBN:0140328726&format=json&jscmd=data"

    response1 = requests.get(url1)
    response2 = requests.get(url2)

    book_data1 = response1.json().get("ISBN:0451526538", {}) if response1.status_code == 200 else {"error": "Failed to fetch"}
    book_data2 = response2.json().get("ISBN:0140328726", {}) if response2.status_code == 200 else {"error": "Failed to fetch"}

    return render(request, 'book.html', {'book1': book_data1, 'book': book_data2})

# Profile View
@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    # Handle form submission for updating user details
    if request.method == 'POST':
        # Create the forms with data from the request
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')

    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
        'profile': profile
    })


@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to profile page after saving changes
    else:
        form = ProfileUpdateForm(instance=profile)
        form = UserUpdateForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form, 'profile': profile})
verification_codes = {}

def forget_password(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        code = str(random.randint(100000, 999999))
        verification_codes[phone] = code

        # Send WhatsApp message
        send_whatsapp_message(phone, f"Your password reset code is: {code}")

        request.session['reset_phone'] = phone
        return redirect('verify_code')
    return render(request, 'forget_password.html')

def verify_code(request):
    phone = request.session.get('reset_phone')
    if request.method == 'POST':
        code = request.POST['code']
        if verification_codes.get(phone) == code:
            return redirect('reset_password')  # a form to input new password
        else:
            messages.error(request, 'Invalid code.')
    return render(request, 'verify_code.html')
import requests

def send_whatsapp_message(phone, message):
    phone = "216" + phone  # Ensure the number is formatted correctly
    token = 'k668mspn3b8leltw'
    instance_id = 'instance114669'
    
    # Token goes in the URL
    url = f"https://api.ultramsg.com/{instance_id}/messages/chat?token={token}"

    payload = {
        "to": phone,
        "body": message,
        "priority": 10,
        "referenceId": "",
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print("📨 UltraMsg Response:", response.status_code, response.text)
    return response.json()
def reset_password(request):
    phone = request.session.get('reset_phone')
    if not phone:
        return redirect('forget_password')

    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 != password2:
            messages.error(request, "Passwords don't match.")
        else:
            try:
                user = User.objects.get(profile__phone=phone)
                user.password = make_password(password1)
                user.save()
                messages.success(request, "Password reset successfully.")
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "No user found with that phone.")
    return render(request, 'reset_password.html')
