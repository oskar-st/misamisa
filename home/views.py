from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser

def homepage(request):
    return render(request, "home.html")

def sklep(request):
    return render(request, "sklep.html")

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # User is active but email not verified
            user.save()
            
            # Send verification email
            verification_url = request.build_absolute_uri(
                f'/verify-email/{user.email_verification_token}/'
            )
            
            # Render email template
            html_message = render_to_string('registration/email_verification.html', {
                'verification_url': verification_url,
            })
            plain_message = strip_tags(html_message)
            
            try:
                print(f"Attempting to send email to: {user.email}")
                print(f"Verification URL: {verification_url}")
                send_mail(
                    subject=_('Verify Your Email - Misamisa'),
                    message=plain_message,
                    from_email=None,  # Uses DEFAULT_FROM_EMAIL
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                print("Email sent successfully!")
                
                return render(request, 'registration/registration_success.html', {
                    'email': user.email
                })
                
            except Exception as e:
                print(f"Email sending failed: {str(e)}")
                # If email fails, still create user but show error
                messages.error(request, _('Account created but verification email could not be sent. Please contact support.'))
                return render(request, 'registration/registration_success.html', {
                    'email': user.email
                })
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def verify_email(request, token):
    """Verify user email with token"""
    try:
        user = CustomUser.objects.get(email_verification_token=token)
        user.email_verified = True
        user.save()
        messages.success(request, _('Email verified successfully! You can now log in.'))
        return redirect('login')
    except CustomUser.DoesNotExist:
        messages.error(request, _('Invalid verification link. Please check your email or contact support.'))
        return redirect('login')

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.email_verified:
                    login(request, user)
                    messages.success(request, _('Logged in successfully!'))
                    return redirect('home')
                else:
                    messages.error(request, _('Please verify your email address before logging in. Check your inbox for the verification email.'))
            else:
                messages.error(request, _('Invalid email or password.'))
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, _('Logged out successfully!'))
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'registration/profile.html')
