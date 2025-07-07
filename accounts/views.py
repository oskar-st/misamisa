from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ShippingAddress, InvoiceDetails
from .forms import ShippingAddressForm, InvoiceDetailsForm

@login_required
def addresses_view(request):
    """Main addresses management page"""
    shipping_addresses = ShippingAddress.objects.filter(user=request.user)
    invoice_details = InvoiceDetails.objects.filter(user=request.user)
    
    context = {
        'shipping_addresses': shipping_addresses,
        'invoice_details': invoice_details,
        'can_add_shipping': shipping_addresses.count() < 6,
        'can_add_invoice': invoice_details.count() < 6,
    }
    
    # Return content-only template for HTMX requests
    if request.headers.get('HX-Request'):
        return render(request, 'accounts/addresses_content.html', context)
    return render(request, 'accounts/addresses.html', context)

@login_required
def add_shipping_address(request):
    """Add new shipping address"""
    # Check if user already has 6 addresses
    if ShippingAddress.objects.filter(user=request.user).count() >= 6:
        messages.error(request, _('Maximum 6 shipping addresses allowed per user'))
        return redirect('addresses')
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Shipping address added successfully'))
                return redirect('addresses')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ShippingAddressForm(user=request.user)
    
    context = {
        'form': form,
        'title': _('Add Shipping Address'),
        'action': 'add',
        'type': 'shipping'
    }
    return render(request, 'accounts/address_form.html', context)

@login_required
def edit_shipping_address(request, address_id):
    """Edit existing shipping address"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Shipping address updated successfully'))
                return redirect('addresses')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ShippingAddressForm(instance=address, user=request.user)
    
    context = {
        'form': form,
        'title': _('Edit Shipping Address'),
        'action': 'edit',
        'type': 'shipping',
        'address': address
    }
    return render(request, 'accounts/address_form.html', context)

@login_required
@require_POST
def delete_shipping_address(request, address_id):
    """Delete shipping address"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address_name = address.full_name
    address.delete()
    messages.success(request, _('Shipping address for "{}" deleted successfully').format(address_name))
    return redirect('addresses')

@login_required
def add_invoice_details(request):
    """Add new invoice details"""
    # Check if user already has 6 invoice details
    if InvoiceDetails.objects.filter(user=request.user).count() >= 6:
        messages.error(request, _('Maximum 6 invoice details allowed per user'))
        return redirect('addresses')
    
    if request.method == 'POST':
        form = InvoiceDetailsForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Invoice details added successfully'))
                return redirect('addresses')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = InvoiceDetailsForm(user=request.user)
    
    context = {
        'form': form,
        'title': _('Add Invoice Details'),
        'action': 'add',
        'type': 'invoice'
    }
    return render(request, 'accounts/address_form.html', context)

@login_required
def edit_invoice_details(request, details_id):
    """Edit existing invoice details"""
    details = get_object_or_404(InvoiceDetails, id=details_id, user=request.user)
    
    if request.method == 'POST':
        form = InvoiceDetailsForm(request.POST, instance=details, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Invoice details updated successfully'))
                return redirect('addresses')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = InvoiceDetailsForm(instance=details, user=request.user)
    
    context = {
        'form': form,
        'title': _('Edit Invoice Details'),
        'action': 'edit',
        'type': 'invoice',
        'details': details
    }
    return render(request, 'accounts/address_form.html', context)

@login_required
@require_POST
def delete_invoice_details(request, details_id):
    """Delete invoice details"""
    details = get_object_or_404(InvoiceDetails, id=details_id, user=request.user)
    details_name = details.full_name_or_company
    details.delete()
    messages.success(request, _('Invoice details for "{}" deleted successfully').format(details_name))
    return redirect('addresses')

@login_required
@require_POST
def set_default_shipping_address(request, address_id):
    """Set shipping address as default"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    
    # Unset all other default addresses for this user
    ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Set this address as default
    address.is_default = True
    address.save()
    
    messages.success(request, _('Default shipping address updated'))
    return redirect('addresses')

@login_required
@require_POST
def set_default_invoice_details(request, details_id):
    """Set invoice details as default"""
    details = get_object_or_404(InvoiceDetails, id=details_id, user=request.user)
    
    # Unset all other default details for this user
    InvoiceDetails.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Set this details as default
    details.is_default = True
    details.save()
    
    messages.success(request, _('Default invoice details updated'))
    return redirect('addresses')
