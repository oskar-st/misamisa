from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from turnstile.fields import TurnstileField
from .models import ShippingAddress, InvoiceDetails

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Enter your email')})
    )
    newsletter_opt_in = forms.BooleanField(
        required=False,
        label=_('Subscribe to newsletter'),
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    turnstile = TurnstileField()

    class Meta:
        model = User
        fields = ('email', 'newsletter_opt_in', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remove username field if it exists
        if 'username' in self.fields:
            del self.fields['username']
            
        # Customize password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Password')
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Confirm Password')
        })
        
        # Remove default help texts
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_('The two password fields didn\'t match.'))
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.newsletter_opt_in = self.cleaned_data.get('newsletter_opt_in', False)
        if commit:
            user.save()
        return user

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'street', 'postal_code', 'city', 'phone', 'email', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Full name')
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Street and number')
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00-000'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('City')
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+48 123 456 789'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Email address')
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'full_name': _('Full name'),
            'street': _('Street and number'),
            'postal_code': _('Postal code'),
            'city': _('City'),
            'phone': _('Phone number'),
            'email': _('Email address'),
            'is_default': _('Set as default')
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        # Check if user already has 6 addresses (only for new addresses)
        if self.user and not self.instance.pk:
            count = ShippingAddress.objects.filter(user=self.user).count()
            if count >= 6:
                raise ValidationError(_('Maximum 6 shipping addresses allowed per user'))
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance

class InvoiceDetailsForm(forms.ModelForm):
    class Meta:
        model = InvoiceDetails
        fields = ['vat_id', 'full_name_or_company', 'street', 'postal_code', 'city', 'is_default']
        widgets = {
            'vat_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXXXXXXXXX'
            }),
            'full_name_or_company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Full name or company name')
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Street and number')
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00-000'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('City')
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'vat_id': _('VAT ID (NIP)'),
            'full_name_or_company': _('Full name or company name'),
            'street': _('Street and number'),
            'postal_code': _('Postal code'),
            'city': _('City'),
            'is_default': _('Set as default')
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add help text for VAT ID
        self.fields['vat_id'].help_text = _('Enter VAT ID if you are buying as a company.')

    def clean(self):
        cleaned_data = super().clean()
        
        # Check if user already has 6 invoice details (only for new entries)
        if self.user and not self.instance.pk:
            count = InvoiceDetails.objects.filter(user=self.user).count()
            if count >= 6:
                raise ValidationError(_('Maximum 6 invoice details allowed per user'))
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance 