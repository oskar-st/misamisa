from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid

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
