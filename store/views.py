from django.contrib.auth import login, authenticate, logout , get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm , ContactForm
from .models import Product , ContactMessage ,CustomUser
from django.core.mail import send_mail,BadHeaderError,EmailMessage
import random
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.messages import get_messages
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from django.db.models.functions import Lower

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')

            # Generate OTP & Expiry (10 minutes)
            otp = random.randint(100000, 999999)
            expiry = (datetime.now() + timedelta(minutes=10)).timestamp()

            # Store OTP data directly in Django Session
            request.session['reg_otp'] = str(otp)
            request.session['reg_otp_expiry'] = expiry
            request.session['pending_email'] = email
            request.session['user_data'] = {
                'email': email,
                'password': form.cleaned_data.get('password1'),
                'name': form.cleaned_data.get('name'),
            }

            # Send Email
            send_mail(
                'Verify Your Email - OTP',
                f'Your OTP for registration is: {otp}. It will expire in 10 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=True,
            )

            messages.success(request, '📧 OTP sent to your email. Please verify.')
            return redirect('verify_email')
        else:
            messages.error(request, '❌ Registration failed. Please check the form.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'auth/register.html', {'form': form})


def verify_email(request):
    email = request.session.get('pending_email')
    stored_otp = request.session.get('reg_otp')
    expiry_timestamp = request.session.get('reg_otp_expiry')

    if not email or not stored_otp:
        messages.error(request, '❌ Session expired. Please register again.')
        return redirect('register')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        # Check OTP Expiry
        if datetime.now().timestamp() > expiry_timestamp:
            # Clean session
            for key in ['reg_otp', 'reg_otp_expiry', 'pending_email', 'user_data']:
                request.session.pop(key, None)
            messages.error(request, '⏰ OTP has expired. Please register again.')
            return redirect('register')

        # Match OTP
        if str(stored_otp) == str(entered_otp):
            data = request.session.get('user_data')
            CustomUser.objects.create_user(
                email=data['email'],
                password=data['password'],
                name=data['name'],
                is_active=True
            )

            # Clear registration session keys
            for key in ['reg_otp', 'reg_otp_expiry', 'pending_email', 'user_data']:
                request.session.pop(key, None)

            messages.success(request, '✅ Email verified! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, '❌ Incorrect OTP.')

    return render(request, 'auth/verify_email.html', {'email': email})

# @login_required(login_url='login')
def home(request):
    products = Product.objects.all()[:3] 
    return render(request, 'index.html', {'products': products})

@login_required(login_url='login')
def product_list(request):
    products = Product.objects.prefetch_related('images').all()

    # Get distinct, non-empty, lowercased descriptions
    fabric_types = (
        Product.objects
        .exclude(Q(description__isnull=True) | Q(description__exact=''))
        .annotate(desc_lower=Lower('description'))
        .values_list('desc_lower', flat=True)
        .distinct()
    )
    print("Distinct Fabric Types:", list(fabric_types))
    return render(request, 'product.html', {
        'products': products,
        'fabric_types': fabric_types,
    })
# @login_required(login_url='login')
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save the message to the database
        ContactMessage.objects.create(name=name, email=email, message=message)

        # Prepare the email content
        subject = f'New Contact Us Message from {name}'
        email_message = f"Sender's Email: {email}\n\nMessage: {message}"
        from_email = 'shreejienterprises84018@gmail.com'  # Your Gmail address
        recipient_list = ['shreejienterprises84018@gmail.com']  # Where you want to receive the email

        try:
            email_object = EmailMessage(
                subject=subject,
                body=email_message,
                from_email=from_email,
                to=recipient_list,
                reply_to=[email],  # Allows you to reply directly to the user
            )
            email_object.send(fail_silently=False)
            return JsonResponse({'success': True})
        except Exception as e:
            print("Email sending error:", str(e))  # Debugging Line - Print the error to console
            return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'store/contact.html')

def error_page(request):
    return render(request, 'store/error_page.html')

# @login_required(login_url='login')
def about(request):
    return render(request, 'about.html')

User = get_user_model()

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if not user.is_active:
                messages.warning(request, "⚠️ Your account is inactive. Contact admin for help.")
                return redirect("login")

            login(request, user)
            messages.success(request, "✅ Login successful! Welcome back.")

            if user.is_superuser:
                return redirect("/admin/")
            else:
                return redirect("home")
        else:
            messages.error(request, "❌ Invalid email or password.")
            return redirect("login")

    return render(request, "auth/login.html")

def logout_view(request):
    # 🔥 Clear all existing messages (like old login messages)
    storage = get_messages(request)
    for _ in storage:
        pass  # this forces clearing old messages

    logout(request)

    messages.success(request, "✅ Logged out successfully!")
    return redirect('login') 

# forgot password 
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)
            expiry = (datetime.now() + timedelta(minutes=10)).timestamp()

            # Store Reset OTP in Django Session
            request.session['reset_email'] = email
            request.session['reset_otp'] = str(otp)
            request.session['reset_otp_expiry'] = expiry

            # Send Email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is {otp}. It will expire in 10 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=True,
            )

            messages.success(request, "✅ OTP has been sent to your email.")
            return redirect('verify_otp')

        except User.DoesNotExist:
            messages.error(request, "❌ Email not registered.")

    return render(request, 'auth/forgot_password.html')

def verify_otp(request):
    email = request.session.get('reset_email')
    stored_otp = request.session.get('reset_otp')
    expiry_timestamp = request.session.get('reset_otp_expiry')

    if not email or not stored_otp:
        messages.error(request, "❌ Invalid session. Please try again.")
        return redirect('forgot_password')

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        # Check Expiry
        if datetime.now().timestamp() > expiry_timestamp:
            for key in ['reset_email', 'reset_otp', 'reset_otp_expiry']:
                request.session.pop(key, None)
            messages.error(request, "⏰ OTP has expired. Please try again.")
            return redirect('forgot_password')

        if str(stored_otp) == str(entered_otp):
            request.session['otp_verified'] = True
            messages.success(request, "✅ OTP verified. You can reset your password now.")
            return redirect('reset_password')
        else:
            messages.error(request, "❌ Invalid OTP.")

    return render(request, 'auth/verify_otp.html')

def reset_password(request):
    if not request.session.get('otp_verified'):
        messages.error(request, "❌ Unauthorized access.")
        return redirect('forgot_password')

    if request.method == "POST":
        email = request.session.get('reset_email')
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password == confirm_password:
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()

                # Clean reset session keys
                for key in ['reset_email', 'reset_otp', 'reset_otp_expiry', 'otp_verified']:
                    request.session.pop(key, None)

                messages.success(request, "✅ Password reset successful. Please log in.")
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "❌ An error occurred. Please try again.")
        else:
            messages.error(request, "❌ Passwords do not match.")

    return render(request, 'auth/reset_password.html')