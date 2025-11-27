from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.forms import Form
from django.http import HttpRequest
from typing import Dict, List, Any
import json
import uuid
from datetime import datetime
from .module import BankWireModule

# Initialize module instance
module = BankWireModule("bank_wire_payment", __file__)

def payment_form(request):
    """Display payment form"""
    try:
        # Get cart items
        cart_items = []
        if hasattr(request, 'user') and request.user.is_authenticated:
            from cookies.models import UserCart
            cart_items = UserCart.objects.filter(user=request.user)
        
        # Get module settings
        settings = module.get_settings()
        
        context = {
            'cart_items': cart_items,
            'bank_details': {
                'bank_name': settings.get('bank_name', ''),
                'account_holder': settings.get('account_holder', ''),
                'account_number': settings.get('account_number', ''),
                'iban': settings.get('iban', ''),
                'swift_code': settings.get('swift_code', ''),
                'additional_info': settings.get('additional_info', '')
            }
        }
        
        return render(request, 'bank_wire_payment/payment_form.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading payment form: {str(e)}")
        return redirect('cart_view')

@csrf_exempt
def payment_process(request):
    """Process payment"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        # Get form data
        form_data = request.POST.dict()
        
        # Validate payment data
        errors = module.validate_payment_data(form_data)
        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        
        # Process payment
        result = module.process_payment(request, form_data)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'redirect_url': result['redirect_url']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Payment processing failed')
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"Payment processing error: {str(e)}"
        })

def payment_success(request):
    """Payment success page"""
    try:
        # Get payment data from session
        payment_data = request.session.get('bank_wire_payment', {})
        
        if not payment_data:
            messages.error(request, "No payment data found")
            return redirect('cart_view')
        
        context = {
            'payment_data': payment_data,
            'reference': payment_data.get('reference', ''),
            'bank_details': payment_data.get('bank_details', {})
        }
        
        # Clear session data
        if 'bank_wire_payment' in request.session:
            del request.session['bank_wire_payment']
        
        return render(request, 'bank_wire_payment/payment_success.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading success page: {str(e)}")
        return redirect('cart_view')

def payment_error(request):
    """Payment error page"""
    try:
        # Get error message from session or request
        error_message = request.session.get('payment_error', 'Payment processing failed')
        
        # Clear session data
        if 'payment_error' in request.session:
            del request.session['payment_error']
        
        context = {
            'error_message': error_message
        }
        
        return render(request, 'bank_wire_payment/payment_error.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading error page: {str(e)}")
        return redirect('cart_view') 