from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser
from .validators import CustomPasswordValidator
# from turnstile.fields import TurnstileField

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter your email')})
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Enter your password')}),
        help_text=_('Your password must be at least 6 characters long and contain at least one uppercase letter and one number.')
    )
    password2 = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Confirm your password')}),
        help_text=_('Enter the same password as before, for verification.')
    )
    # captcha = TurnstileField(
    #     label=_('Security Check'),
    #     help_text=_('Please complete the security check to verify you are human.')
    # )

    class Meta:
        model = CustomUser
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].validators.append(CustomPasswordValidator())

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter your email')})
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Enter your password')})
    ) 