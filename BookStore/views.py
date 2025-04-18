from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
import requests
import random

from .forms import UserUpdateForm
from .utils import check_password_strength

User = get_user_model()  # Custom user model
verification_codes = {}

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
        address = request.POST.get('address')
        phone = request.POST.get('phone')
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
                address=address, 
                phone=phone,
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

# Login View
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

# Logout View
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('login')

# Home View
def home(request):
    return render(request, 'home.html')

# Profile View
@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'profile.html', {'form': form, 'user': user})

# Edit Profile View
@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get('password')

            if new_password:
                print(f"Old password: {user.password}")  # Print old password (hashed)
                user.set_password(new_password)
                print(f"New password: {user.password}")  # Print new password (hashed)

            user.save()

            if new_password:
                login(request,user)

            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'edit_profile.html', {'form': form, 'user': user})

# Forgot Password View
def forget_password(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        code = str(random.randint(100000, 999999))
        verification_codes[phone] = code
        send_whatsapp_message(phone, f"Your password reset code is: {code}")
        request.session['reset_phone'] = phone
        return redirect('verify_code')
    return render(request, 'forget_password.html')

# Verify Code View
def verify_code(request):
    phone = request.session.get('reset_phone')
    if request.method == 'POST':
        code = request.POST['code']
        if verification_codes.get(phone) == code:
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid code.')
    return render(request, 'verify_code.html')

# Send WhatsApp Message
def send_whatsapp_message(phone, message):
    phone = "216" + phone
    token = 'k668mspn3b8leltw'
    instance_id = 'instance114669'

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

# Reset Password View
def reset_password(request):
    phone = request.session.get('reset_phone')
    if not phone:
        messages.error(request, "Session expired. Try again.")
        return redirect('forget_password')

    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        print("📌 Password 1:", password1)
        print("📌 Password 2:", password2)

        if password1 != password2:
            messages.error(request, "Passwords don't match.")
        else:
            try:
                user = User.objects.get(phone=phone)
                print("✅ User found:", user.username)

                user.set_password(password1)
                user.save()
                print("✅ Password reset and saved!")

                messages.success(request, "Password reset successfully.")
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "No user found with that phone.")
                print("❌ No user found with phone:", phone)

    return render(request, 'reset_password.html')
