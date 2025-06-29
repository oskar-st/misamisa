"""
Stripe Payment Form
"""
from django import forms


class StripePaymentForm(forms.Form):
    """Stripe payment form."""
    
    email = forms.EmailField(
        label='Email address',
        help_text='We\'ll send you a receipt to this email address.',
        required=True
    )
    
    name = forms.CharField(
        label='Name on card',
        max_length=255,
        required=True
    )
    
    stripe_token = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    def clean(self):
        """Clean and validate form data."""
        cleaned_data = super().clean()
        
        # Add any additional validation here
        email = cleaned_data.get('email')
        name = cleaned_data.get('name')
        stripe_token = cleaned_data.get('stripe_token')
        
        if not email:
            raise forms.ValidationError('Email is required.')
        
        if not name:
            raise forms.ValidationError('Name is required.')
        
        if not stripe_token:
            raise forms.ValidationError('Payment information is required.')
        
        return cleaned_data 