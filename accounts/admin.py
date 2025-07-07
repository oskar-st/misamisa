from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import CustomUser, ShippingAddress, InvoiceDetails, Address

# Completely disable default Django user admin registration
from django.contrib.auth.models import User as DjangoUser

# Prevent any auto-registration of User admin
try:
    # Unregister Django's default User if registered
    if admin.site.is_registered(DjangoUser):
        admin.site.unregister(DjangoUser)
except:
    pass

try:
    # Force unregister any existing User admin  
    User = get_user_model()
    if admin.site.is_registered(User):
        admin.site.unregister(User)
except:
    pass

# Clear any cached admin registrations that might cause conflicts
admin.site._registry = {k: v for k, v in admin.site._registry.items() 
                       if k.__name__ not in ['User', 'CustomUser']}

class CustomUserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field."""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'email_verified', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'email_verified', 'newsletter_opt_in', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Email verification'), {'fields': ('email_verified', 'email_verification_token')}),
        (_('Preferences'), {'fields': ('newsletter_opt_in',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'newsletter_opt_in'),
        }),
    )
    
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login', 'email_verification_token')
    filter_horizontal = ('groups', 'user_permissions')
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'city', 'postal_code', 'phone', 'is_default', 'created_at')
    list_filter = ('is_default', 'city', 'created_at')
    search_fields = ('full_name', 'user__email', 'street', 'city', 'phone', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'full_name', 'email')
        }),
        (_('Address'), {
            'fields': ('street', 'postal_code', 'city')
        }),
        (_('Contact'), {
            'fields': ('phone',)
        }),
        (_('Settings'), {
            'fields': ('is_default',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = CustomUser.objects.filter(is_active=True).order_by('email')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(InvoiceDetails)
class InvoiceDetailsAdmin(admin.ModelAdmin):
    list_display = ('full_name_or_company', 'user', 'vat_id', 'city', 'postal_code', 'is_default', 'created_at')
    list_filter = ('is_default', 'city', 'created_at')
    search_fields = ('full_name_or_company', 'user__email', 'vat_id', 'street', 'city')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'full_name_or_company')
        }),
        (_('Tax Information'), {
            'fields': ('vat_id',),
            'description': _('Enter VAT ID if this is a company purchase')
        }),
        (_('Address'), {
            'fields': ('street', 'postal_code', 'city')
        }),
        (_('Settings'), {
            'fields': ('is_default',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = CustomUser.objects.filter(is_active=True).order_by('email')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Keep the old Address admin for backward compatibility
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'address_type', 'city', 'country', 'is_default', 'created_at')
    list_filter = ('address_type', 'is_default', 'country', 'created_at')
    search_fields = ('name', 'user__email', 'company_name', 'street', 'city', 'country')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'address_type', 'name', 'company_name')
        }),
        (_('Tax Information'), {
            'fields': ('tax_id',)
        }),
        (_('Address'), {
            'fields': ('street', 'city', 'postcode', 'country')
        }),
        (_('Contact'), {
            'fields': ('phone',)
        }),
        (_('Settings'), {
            'fields': ('is_default',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
