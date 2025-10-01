from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ShippingMethod
from modules.manager import module_manager


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

    # Private buyer shipping address
    shipping_full_name = forms.CharField(max_length=100, required=False, label=_('Imię i nazwisko'))
    shipping_street = forms.CharField(max_length=200, required=False, label=_('Ulica i numer'))
    shipping_postal_code = forms.CharField(max_length=6, required=False, label=_('Kod pocztowy'))
    shipping_city = forms.CharField(max_length=100, required=False, label=_('Miasto'))
    shipping_phone = forms.CharField(max_length=20, required=False, label=_('Telefon'))
    shipping_email = forms.EmailField(required=False, label=_('E-mail'))

    # Company invoice details
    invoice_vat_id = forms.CharField(max_length=15, required=False, label=_('NIP'))
    invoice_company_name = forms.CharField(max_length=200, required=False, label=_('Nazwa firmy'))
    invoice_street = forms.CharField(max_length=200, required=False, label=_('Ulica i numer'))
    invoice_postal_code = forms.CharField(max_length=6, required=False, label=_('Kod pocztowy'))
    invoice_city = forms.CharField(max_length=100, required=False, label=_('Miasto'))
    delivery_same_as_invoice = forms.BooleanField(required=False, initial=True, label=_('Adres dostawy taki sam jak firmowy'))

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
            required = ['shipping_full_name', 'shipping_street', 'shipping_postal_code', 'shipping_city', 'shipping_phone', 'shipping_email']
            for f in required:
                if not cleaned.get(f):
                    self.add_error(f, _('To pole jest wymagane.'))
        elif buyer_type == 'company':
            required = ['invoice_company_name', 'invoice_street', 'invoice_postal_code', 'invoice_city']
            for f in required:
                if not cleaned.get(f):
                    self.add_error(f, _('To pole jest wymagane.'))
            if not cleaned.get('delivery_same_as_invoice'):
                delivery_fields = ['delivery_full_name', 'delivery_street', 'delivery_postal_code', 'delivery_city', 'delivery_phone', 'delivery_email']
                for f in delivery_fields:
                    if not cleaned.get(f):
                        self.add_error(f, _('To pole jest wymagane.'))
        return cleaned


class OrderSummaryForm(forms.Form):
    want_to_add_comment = forms.BooleanField(required=False, label=_('Chcę dodać komentarz'))
    order_comment = forms.CharField(required=False, widget=forms.Textarea, label=_('Komentarz do zamówienia'))


