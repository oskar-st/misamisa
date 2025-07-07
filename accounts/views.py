from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
import re
from .models import ShippingAddress, InvoiceDetails, validate_polish_nip
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
        return redirect('accounts:addresses')
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Shipping address added successfully'))
                return redirect('accounts:addresses')
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
                return redirect('accounts:addresses')
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
    return redirect('accounts:addresses')

@login_required
def add_invoice_details(request):
    """Add new invoice details"""
    # Check if user already has 6 invoice details
    if InvoiceDetails.objects.filter(user=request.user).count() >= 6:
        messages.error(request, _('Maximum 6 invoice details allowed per user'))
        return redirect('accounts:addresses')
    
    if request.method == 'POST':
        form = InvoiceDetailsForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, _('Invoice details added successfully'))
                return redirect('accounts:addresses')
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
                return redirect('accounts:addresses')
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
    return redirect('accounts:addresses')

@require_GET
@csrf_exempt
def validate_nip_api(request):
    """API endpoint to validate NIP against GUS database"""
    try:
        nip = request.GET.get('nip', '').strip()
        
        if not nip:
            return JsonResponse({'valid': False, 'error': 'NIP jest wymagany'})
        
        # Clean the NIP (remove spaces, dashes, etc.)
        cleaned_nip = re.sub(r'[^\d]', '', nip)
        
        if len(cleaned_nip) != 10:
            return JsonResponse({'valid': False, 'error': 'NIP musi mieć dokładnie 10 cyfr'})
        
        # First validate checksum locally
        try:
            validate_polish_nip(cleaned_nip)
        except ValidationError as e:
            return JsonResponse({'valid': False, 'error': 'Nieprawidłowa suma kontrolna NIP'})
        
        # Try to check against GUS API
        gus_result = check_nip_in_gus(cleaned_nip)
        print(f"GUS check result for {cleaned_nip}: {gus_result}")
        
        if isinstance(gus_result, dict) and gus_result.get('found'):
            # GUS returned company data
            return JsonResponse({
                'valid': True, 
                'message': '✅ NIP zweryfikowany i aktywny w bazie GUS',
                'nip': cleaned_nip,
                'gus_verified': True,
                'company_data': gus_result.get('data', {})
            })
        elif gus_result is True:
            return JsonResponse({
                'valid': True, 
                'message': '✅ NIP zweryfikowany i aktywny w bazie GUS',
                'nip': cleaned_nip,
                'gus_verified': True
            })
        elif gus_result is False:
            # NIP not found in GUS (404) - treat as invalid even if checksum is correct
            return JsonResponse({
                'valid': False, 
                'error': '❌ NIP nie znaleziony w bazie GUS (może nie istnieć)',
                'nip': cleaned_nip,
                'gus_verified': False
            })
        else:
            # GUS API unavailable, but checksum is valid
            # Provide helpful feedback about NIP structure
            is_likely_test = (
                cleaned_nip.startswith(('1111', '0000', '9999')) or 
                cleaned_nip == '1234567890' or
                cleaned_nip in ['1111111111', '0000000000', '9999999999']
            )
            
            # Check if it's a well-known real company (basic whitelist)
            known_real_nips = {
                '5252651120': 'Microsoft Poland',
                '8992717839': 'Google Poland', 
                '9492107026': 'x-kom',
                '7010144598': 'Allegro.pl',
                '5213017654': 'CD Projekt',
            }
            
            if cleaned_nip in known_real_nips:
                company_name = known_real_nips[cleaned_nip]
                return JsonResponse({
                    'valid': True, 
                    'message': f'✅ Suma kontrolna prawidłowa ({company_name} - GUS niedostępny)',
                    'nip': cleaned_nip,
                    'gus_verified': False
                })
            elif is_likely_test:
                return JsonResponse({
                    'valid': True, 
                    'message': '⚠️ Suma kontrolna prawidłowa (prawdopodobnie testowy NIP)',
                    'nip': cleaned_nip,
                    'gus_verified': False
                })
            else:
                return JsonResponse({
                    'valid': True, 
                    'message': '✅ Suma kontrolna prawidłowa (weryfikacja GUS niedostępna)',
                    'nip': cleaned_nip,
                    'gus_verified': False
                })
            
    except Exception as e:
        return JsonResponse({'valid': False, 'error': f'Błąd serwera: {str(e)}'})

def check_nip_in_gus(nip):
    """Check NIP in GUS (Polish tax authority) database"""
    try:
        import urllib.request
        import urllib.parse
        import json
        import ssl
        import socket
        from datetime import date
        
        # Use current date, but ensure it's within the 5-year limit
        from datetime import datetime, timedelta
        today = datetime.now().date()
        
        # API supports dates from last 5 years, use a recent date that should work
        check_date = today.strftime('%Y-%m-%d')
        url = f"https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={check_date}"
        
        print(f"Checking NIP {nip} with GUS API: {url}")
        
        # First test basic connectivity
        try:
            socket.setdefaulttimeout(5)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('wl-api.mf.gov.pl', 443))
            print("✓ Basic connectivity to GUS API server OK")
        except Exception as conn_err:
            print(f"✗ Cannot connect to GUS API server: {conn_err}")
            return None
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        
        # Create request with proper headers
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        req.add_header('Accept', 'application/json')
        req.add_header('Accept-Language', 'pl-PL,pl;q=0.9,en;q=0.8')
        
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            response_text = response.read().decode('utf-8')
            print(f"✓ GUS API response received (status: {response.status})")
            
            if response.status == 200:
                try:
                    data = json.loads(response_text)
                    print(f"✓ JSON parsed successfully")
                    
                    # According to API docs: result.subject exists if NIP found
                    if data.get('result') and data['result'].get('subject'):
                        subject = data['result']['subject']
                        # Check if actively registered (statusVat = "Czynny")
                        status = subject.get('statusVat', '')
                        name = subject.get('name', 'N/A')
                        print(f"✓ Found: {name}, Status: {status}")
                        
                        if status == 'Czynny':
                            # Extract company data for autofill
                            working_address = subject.get('workingAddress', '')
                            
                            # For individual businesses, try other address fields if workingAddress is empty
                            residence_address = subject.get('residenceAddress', '')  # Fixed: was 'residencyAddress'
                            registered_address = subject.get('registeredAddress', '')
                            
                            # Also check Polish field names and alternative spellings
                            adres_zamieszkania = subject.get('adresZamieszkania', '')
                            adres_siedziby = subject.get('adresSiedziby', '')
                            adres = subject.get('adres', '')
                            
                            # Print ALL available fields to debug
                            print(f"=== COMPLETE GUS RESPONSE ANALYSIS ===")
                            print(f"Available subject fields: {list(subject.keys())}")
                            print(f"Total fields count: {len(subject.keys())}")
                            
                            # Print all fields with their values
                            print("All field values:")
                            for key, value in subject.items():
                                if isinstance(value, str):
                                    print(f"  {key}: '{value}'")
                                else:
                                    print(f"  {key}: {value}")
                            
                            print(f"\n=== ADDRESS FIELD ANALYSIS ===")
                            address_candidates = {
                                'workingAddress': working_address,
                                'residenceAddress': residence_address,  # Fixed: was 'residencyAddress'
                                'registeredAddress': registered_address,
                                'adresZamieszkania': adres_zamieszkania,
                                'adresSiedziby': adres_siedziby,
                                'adres': adres
                            }
                            
                            for field_name, field_value in address_candidates.items():
                                if field_value:
                                    print(f"  ✓ {field_name}: '{field_value}'")
                                else:
                                    print(f"  ✗ {field_name}: (empty or missing)")
                            
                            # Use the first available address (try all possible field names)
                            address_to_parse = (working_address or residence_address or registered_address or 
                                              adres_zamieszkania or adres_siedziby or adres)
                            
                            company_data = {
                                'name': name,
                                'working_address': working_address,
                                'residence_address': residence_address,  # Fixed: was 'residency_address'
                                'registered_address': registered_address,
                                'parsed_from': 'working_address' if working_address else ('residence_address' if residence_address else ('registered_address' if registered_address else 'none'))
                            }
                            
                            # Try to parse the address into components
                            if address_to_parse:
                                import re
                                print(f"Parsing address from {company_data['parsed_from']}: '{address_to_parse}'")
                                
                                # Try multiple address formats that GUS might return:
                                # Format 1: "STREET NUMBER, POSTAL_CODE CITY" (companies)
                                # Format 2: "STREET NUMBER POSTAL_CODE CITY" (individual businesses)
                                # Format 3: "ul. STREET NUMBER, POSTAL_CODE CITY"
                                
                                # First, try to find postal code and city (most reliable part)
                                postal_city_match = re.search(r'(\d{2}-\d{3})\s+([^,]+?)(?:,|$)', address_to_parse)
                                if postal_city_match:
                                    postal_code = postal_city_match.group(1)
                                    city = postal_city_match.group(2).strip()
                                    company_data['postal_code'] = postal_code
                                    company_data['city'] = city
                                    print(f"✓ Found postal code: '{postal_code}', city: '{city}'")
                                else:
                                    print("✗ Could not extract postal code and city")
                                
                                # Now try to extract street address
                                street = None
                                
                                # Method 1: Street before comma and postal code
                                street_match = re.search(r'^(.+?)(?=\s*,\s*\d{2}-\d{3})', address_to_parse)
                                if street_match:
                                    street = street_match.group(1).strip()
                                    print(f"✓ Street extracted (method 1): '{street}'")
                                else:
                                    # Method 2: Street before postal code (no comma)
                                    street_match = re.search(r'^(.+?)(?=\s+\d{2}-\d{3})', address_to_parse)
                                    if street_match:
                                        street = street_match.group(1).strip()
                                        print(f"✓ Street extracted (method 2): '{street}'")
                                    else:
                                        # Method 3: Take everything before postal code as fallback
                                        parts = re.split(r'\s*\d{2}-\d{3}', address_to_parse)
                                        if len(parts) > 0 and parts[0].strip():
                                            street = parts[0].strip()
                                            print(f"✓ Street extracted (method 3): '{street}'")
                                        else:
                                            print("✗ Could not extract street address")
                                
                                # Clean up the street if we found one
                                if street:
                                    # Remove common prefixes like "ul.", "al.", etc.
                                    street = re.sub(r'^(ul\.|al\.|pl\.|os\.)\s*', '', street, flags=re.IGNORECASE)
                                    # Remove trailing comma if present
                                    street = street.rstrip(',').strip()
                                    
                                    if street:  # Make sure we still have something after cleaning
                                        company_data['street'] = street
                                        print(f"✓ Final street: '{street}'")
                                    else:
                                        print("✗ Street became empty after cleaning")
                            else:
                                print("✗ No address data available from GUS (checked workingAddress, residenceAddress, registeredAddress)")
                                company_data['address_note'] = 'no_address_available'
                            
                            print(f"✓ Company data extracted: {company_data}")
                            return {'found': True, 'data': company_data}
                        else:
                            print(f"✗ NIP inactive, status: {status}")
                            return False
                    else:
                        print("✗ NIP not found in GUS database")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"✗ JSON parsing error: {e}")
                    return None
            else:
                print(f"✗ HTTP error status: {response.status}")
                return None
        
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP Error: {e.code} - {e.reason}")
        print(f"✗ URL that failed: {url}")
        
        if e.code == 404:
            print(f"✗ 404 Error - NIP nie został znaleziony w bazie GUS")
            print(f"  - NIP może nie istnieć w bazie GUS")
            print(f"  - NIP może nie być aktywny w dniu {check_date}")
            return False  # NIP not found in GUS, but checksum was valid
            
        try:
            error_body = e.read().decode('utf-8')
            print(f"✗ Error response body: {error_body}")
        except:
            pass
            
        return None  # Other HTTP errors
        
    except urllib.error.URLError as e:
        print(f"✗ URL Error: {e.reason}")
        return None
        
    except socket.timeout:
        print(f"✗ Timeout connecting to GUS API")
        return None
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None


