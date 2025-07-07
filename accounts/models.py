from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import uuid
import re

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    is_superuser = models.BooleanField(_('superuser status'), default=False)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    email_verified = models.BooleanField(_('email verified'), default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    newsletter_opt_in = models.BooleanField(_('newsletter opt-in'), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

def validate_polish_postcode(value):
    """Validate Polish postal code format (XX-XXX)"""
    if not re.match(r'^\d{2}-\d{3}$', value):
        raise ValidationError(
            _('Polish postal code must be in format XX-XXX (e.g., 00-001)'),
            code='invalid_postcode'
        )

def validate_polish_phone(value):
    """Validate Polish phone number"""
    # Remove spaces and other characters
    cleaned = re.sub(r'[^\d+]', '', value)
    
    # Check if it's a valid Polish phone number
    if not (
        re.match(r'^\+48\d{9}$', cleaned) or  # +48XXXXXXXXX
        re.match(r'^48\d{9}$', cleaned) or   # 48XXXXXXXXX
        re.match(r'^\d{9}$', cleaned) or     # XXXXXXXXX
        re.match(r'^\d{3}\d{3}\d{3}$', cleaned)  # XXX XXX XXX
    ):
        raise ValidationError(
            _('Enter a valid Polish phone number'),
            code='invalid_phone'
        )

def validate_polish_nip(value):
    """Validate Polish NIP (Tax ID)"""
    if not value:
        return  # NIP is optional
    
    # Remove spaces and dashes
    cleaned = re.sub(r'[^\d]', '', value)
    
    if len(cleaned) != 10:
        raise ValidationError(
            _('Polish NIP must have exactly 10 digits'),
            code='invalid_nip'
        )
    
    # NIP checksum validation
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    checksum = sum(int(digit) * weight for digit, weight in zip(cleaned[:9], weights)) % 11
    
    if checksum != int(cleaned[9]):
        raise ValidationError(
            _('Invalid NIP checksum'),
            code='invalid_nip'
        )

class ShippingAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shipping_addresses',
        verbose_name=_('user')
    )
    full_name = models.CharField(_('full name'), max_length=100)
    street = models.CharField(_('street and number'), max_length=200)
    postal_code = models.CharField(
        _('postal code'), 
        max_length=6,
        validators=[validate_polish_postcode],
        help_text=_('Format: XX-XXX')
    )
    city = models.CharField(_('city'), max_length=100)
    phone = models.CharField(
        _('phone number'), 
        max_length=20,
        validators=[validate_polish_phone],
        help_text=_('Polish phone number')
    )
    email = models.EmailField(_('email address'))
    is_default = models.BooleanField(_('is default'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('shipping address')
        verbose_name_plural = _('shipping addresses')
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.city}"

    def save(self, *args, **kwargs):
        # Check maximum limit (6 addresses per user)
        if not self.pk:  # Only check for new addresses
            count = ShippingAddress.objects.filter(user=self.user).count()
            if count >= 6:
                raise ValidationError(_('Maximum 6 shipping addresses allowed per user'))
        
        # If this address is set as default, unset other default addresses for this user
        if self.is_default:
            ShippingAddress.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)

class InvoiceDetails(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoice_details',
        verbose_name=_('user')
    )
    vat_id = models.CharField(
        _('VAT ID (NIP)'), 
        max_length=15, 
        blank=True,
        validators=[validate_polish_nip],
        help_text=_('Enter VAT ID if you\'re buying as a company.')
    )
    full_name_or_company = models.CharField(_('full name or company name'), max_length=200)
    street = models.CharField(_('street and number'), max_length=200)
    postal_code = models.CharField(
        _('postal code'), 
        max_length=6,
        validators=[validate_polish_postcode],
        help_text=_('Format: XX-XXX')
    )
    city = models.CharField(_('city'), max_length=100)
    is_default = models.BooleanField(_('is default'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('invoice details')
        verbose_name_plural = _('invoice details')
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name_or_company} - {self.city}"

    def save(self, *args, **kwargs):
        # Check maximum limit (6 invoice details per user)
        if not self.pk:  # Only check for new entries
            count = InvoiceDetails.objects.filter(user=self.user).count()
            if count >= 6:
                raise ValidationError(_('Maximum 6 invoice details allowed per user'))
        
        # If this entry is set as default, unset other default entries for this user
        if self.is_default:
            InvoiceDetails.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)

# Keep the old Address model for backward compatibility
class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('shipping', _('Shipping')),
        ('billing', _('Billing')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('user')
    )
    address_type = models.CharField(
        _('address type'),
        max_length=10,
        choices=ADDRESS_TYPE_CHOICES,
        default='shipping'
    )
    is_default = models.BooleanField(_('is default'), default=False)
    name = models.CharField(_('name'), max_length=100)
    company_name = models.CharField(_('company name'), max_length=100, blank=True)
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True)
    street = models.CharField(_('street'), max_length=200)
    city = models.CharField(_('city'), max_length=100)
    postcode = models.CharField(_('postcode'), max_length=20)
    country = models.CharField(_('country'), max_length=100)
    phone = models.CharField(_('phone'), max_length=20)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.address_type} ({self.city}, {self.country})"

    def save(self, *args, **kwargs):
        # If this address is set as default, unset other default addresses of the same type for this user
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
