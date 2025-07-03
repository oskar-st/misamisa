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
from accounts.models import CustomUser
from home.models import News

def homepage(request):
    news_items = News.objects.all()
    context = {"news_items": news_items}
    
    # For htmx requests, return just the main content
    if request.headers.get('HX-Request'):
        return render(request, 'home_content.html', context)
    
    return render(request, "home.html", context)

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
                
                context = {'email': user.email}
                if request.headers.get('HX-Request'):
                    return render(request, 'registration/registration_success_content.html', context)
                return render(request, 'registration/registration_success.html', context)
                
            except Exception as e:
                print(f"Email sending failed: {str(e)}")
                # If email fails, still create user but show error
                messages.error(request, _('Account created but verification email could not be sent. Please contact support.'))
                context = {'email': user.email}
                if request.headers.get('HX-Request'):
                    return render(request, 'registration/registration_success_content.html', context)
                return render(request, 'registration/registration_success.html', context)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form}
    if request.headers.get('HX-Request'):
        return render(request, 'registration/register_content.html', context)
    return render(request, 'registration/register.html', context)

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
    
    context = {'form': form}
    if request.headers.get('HX-Request'):
        return render(request, 'registration/login_content.html', context)
    return render(request, 'registration/login.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, _('Logged out successfully!'))
    return redirect('home')

@login_required
def profile_view(request):
    context = {}
    if request.headers.get('HX-Request'):
        return render(request, 'registration/profile_content.html', context)
    return render(request, 'registration/profile.html', context)

def resend_verification_email(request):
    from django.contrib.auth import get_user_model
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            if user.email_verified:
                from django.contrib import messages
                messages.info(request, _('Your email is already verified. You can log in.'))
                return render(request, 'registration/resend_verification.html', {'email': email})
            verification_url = request.build_absolute_uri(f'/verify-email/{user.email_verification_token}/')
            html_message = render_to_string('registration/email_verification.html', {'verification_url': verification_url})
            plain_message = strip_tags(html_message)
            send_mail(
                subject=_('Verify Your Email - Misamisa'),
                message=plain_message,
                from_email=None,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            from django.contrib import messages
            messages.success(request, _('Verification email resent. Please check your inbox.'))
            return render(request, 'registration/resend_verification.html', {'email': email})
        except User.DoesNotExist:
            from django.contrib import messages
            messages.error(request, _('No user found with that email address.'))
            return render(request, 'registration/resend_verification.html', {'email': email})
    return render(request, 'registration/resend_verification.html')

def contact_view(request):
    """Contact page view"""
    context = {'title': _('Contact Us')}
    if request.headers.get('HX-Request'):
        return render(request, 'contact_content.html', context)
    return render(request, 'contact.html', context)

def about_view(request):
    """About page view"""
    context = {'title': _('About Us')}
    if request.headers.get('HX-Request'):
        return render(request, 'about_content.html', context)
    return render(request, 'about.html', context)

def terms_view(request):
    """Terms of Service page view"""
    context = {'title': _('Terms of Service')}
    if request.headers.get('HX-Request'):
        return render(request, 'terms_content.html', context)
    return render(request, 'terms.html', context)

def privacy_view(request):
    """Privacy Policy page view"""
    context = {'title': _('Privacy Policy')}
    if request.headers.get('HX-Request'):
        return render(request, 'privacy_content.html', context)
    return render(request, 'privacy.html', context)
