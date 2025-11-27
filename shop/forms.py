from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ShippingMethod
from modules.manager import module_manager
from accounts.models import ShippingAddress, InvoiceDetails


class CheckoutShippingPaymentForm(forms.Form):
    """Step 2 form: shipping method, buyer type, addresses, payment method."""

    BUYER_TYPE_CHOICES = [
        ('private', _('Osoba prywatna')),
        ('company', _('Firma')),
    ]

    shipping_method = forms.ModelChoiceField(
        queryset=ShippingMethod.objects.filter(is_active=True),
        widget=forms.RadioSelect,
        label=_('Sposób dostawy'),
        empty_label=None,
    )

    buyer_type = forms.ChoiceField(
        choices=BUYER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label=_('Kupujesz jako'),
        initial='private',
    )

    # Address selection fields
    selected_shipping_address = forms.ModelChoiceField(
        queryset=ShippingAddress.objects.none(),
        required=False,
        empty_label=_('Select a shipping address'),
        label=_('Saved shipping addresses'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    selected_delivery_address = forms.ModelChoiceField(
        queryset=ShippingAddress.objects.none(),
        required=False,
        empty_label=_('Select a shipping address'),
        label=_('Select delivery address'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    selected_invoice_details = forms.ModelChoiceField(
        queryset=InvoiceDetails.objects.none(),
        required=False,
        empty_label=_('Select invoice details'),
        label=_('Saved invoice details'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Private buyer shipping address (fallback form)
    shipping_full_name = forms.CharField(max_length=100, required=False, label=_('Imię i nazwisko'))
    shipping_street = forms.CharField(max_length=200, required=False, label=_('Ulica i numer'))
    shipping_postal_code = forms.CharField(max_length=6, required=False, label=_('Kod pocztowy'))
    shipping_city = forms.CharField(max_length=100, required=False, label=_('Miasto'))
    shipping_phone = forms.CharField(max_length=20, required=False, label=_('Telefon'))
    shipping_email = forms.EmailField(required=False, label=_('E-mail'))

    # Company invoice details (fallback form)
    invoice_vat_id = forms.CharField(max_length=15, required=False, label=_('NIP'))
    invoice_company_name = forms.CharField(max_length=200, required=False, label=_('Nazwa firmy'))
    invoice_street = forms.CharField(max_length=200, required=False, label=_('Ulica i numer'))
    invoice_postal_code = forms.CharField(max_length=6, required=False, label=_('Kod pocztowy'))
    invoice_city = forms.CharField(max_length=100, required=False, label=_('Miasto'))
    # Company delivery address (if different)
    delivery_full_name = forms.CharField(max_length=100, required=False, label=_('Imię i nazwisko'))
    delivery_street = forms.CharField(max_length=200, required=False, label=_('Ulica i numer'))
    delivery_postal_code = forms.CharField(max_length=6, required=False, label=_('Kod pocztowy'))
    delivery_city = forms.CharField(max_length=100, required=False, label=_('Miasto'))
    delivery_phone = forms.CharField(max_length=20, required=False, label=_('Telefon'))
    delivery_email = forms.EmailField(required=False, label=_('E-mail'))

    payment_method = forms.CharField(label=_('Sposób płatności'), widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Populate address selection fields if user is provided
        if self.user:
            shipping_qs = ShippingAddress.objects.filter(user=self.user)
            invoice_qs = InvoiceDetails.objects.filter(user=self.user)
            self.fields['selected_shipping_address'].queryset = shipping_qs
            self.fields['selected_delivery_address'].queryset = shipping_qs
            self.fields['selected_invoice_details'].queryset = invoice_qs
        else:
            shipping_qs = self.fields['selected_shipping_address'].queryset
            invoice_qs = self.fields['selected_invoice_details'].queryset
        
        self.has_saved_shipping_addresses = shipping_qs.exists()
        self.has_saved_invoice_details = invoice_qs.exists()

        # Populate payment choices from modules
        choices = []
        for code, module in module_manager.get_payment_modules().items():
            if module.is_installed and module.is_enabled:
                choices.append((code, getattr(module, 'display_name', code.title())))
        self.fields['payment_method'].widget.choices = choices

    def clean(self):
        cleaned = super().clean()
        buyer_type = cleaned.get('buyer_type')
        
        if buyer_type == 'private':
            selected_address = cleaned.get('selected_shipping_address')
            if self.has_saved_shipping_addresses:
                if not selected_address:
                    self.add_error('selected_shipping_address', _('Select a shipping address.'))
            else:
                # Validate manual address fields when no saved addresses exist
                required = ['shipping_full_name', 'shipping_street', 'shipping_postal_code', 'shipping_city', 'shipping_phone', 'shipping_email']
                for f in required:
                    if not cleaned.get(f):
                        self.add_error(f, _('To pole jest wymagane.'))
                        
        elif buyer_type == 'company':
            # Check if user selected saved invoice details or wants to use new details
            selected_invoice = cleaned.get('selected_invoice_details')
            
            if self.has_saved_invoice_details:
                if not selected_invoice:
                    self.add_error('selected_invoice_details', _('Select invoice details.'))
            else:
                # Validate manual invoice fields
                required = ['invoice_company_name', 'invoice_street', 'invoice_postal_code', 'invoice_city']
                for f in required:
                    if not cleaned.get(f):
                        self.add_error(f, _('To pole jest wymagane.'))
                        
            # Handle delivery address for companies
            selected_delivery = cleaned.get('selected_delivery_address')
            delivery_fields = ['delivery_full_name', 'delivery_street', 'delivery_postal_code', 'delivery_city', 'delivery_phone', 'delivery_email']
            manual_delivery_values = [cleaned.get(f) for f in delivery_fields]
            manual_delivery_provided = any(manual_delivery_values)
            
            if manual_delivery_provided:
                for f in delivery_fields:
                    if not cleaned.get(f):
                        self.add_error(f, _('To pole jest wymagane.'))
            
            cleaned['delivery_same_as_invoice'] = not (selected_delivery or manual_delivery_provided)
                            
        return cleaned


class OrderSummaryForm(forms.Form):
    want_to_add_comment = forms.BooleanField(required=False, label=_('Chcę dodać komentarz'))
    order_comment = forms.CharField(required=False, widget=forms.Textarea, label=_('Komentarz do zamówienia'))


