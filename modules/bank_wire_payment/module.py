from modules.base import PaymentModuleBase
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.forms import Form
from django.http import HttpRequest
from typing import Dict, List, Any, Optional
import json
import uuid
import os
from datetime import datetime

class BankWireModule(PaymentModuleBase):
    def __init__(self, module_name: str, module_path: str):
        super().__init__(module_name, module_path)
        
    def get_admin_config(self) -> Optional[str]:
        """Get admin configuration template path"""
        if self.manifest and self.manifest.admin_config:
            admin_path = os.path.join(self.module_path, 'templates', self.module_name, 'admin', 'config.html')
            if os.path.exists(admin_path):
                return f"{self.module_name}/admin/config.html"
        return None
        
    def install(self) -> bool:
        """Install the module"""
        try:
            # Add installation logic here if needed
            return True
        except Exception as e:
            print(f"Installation error: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall the module"""
        try:
            # Add uninstallation logic here if needed
            return True
        except Exception as e:
            print(f"Uninstallation error: {e}")
            return False
    
    def enable(self) -> bool:
        """Enable the module"""
        self.is_enabled = True
        return True
    
    def disable(self) -> bool:
        """Disable the module"""
        self.is_enabled = False
        return True
        
    def get_payment_form(self) -> Form:
        """Return the payment form class"""
        # For now, return a simple form class
        from django import forms
        class BankWireForm(forms.Form):
            confirm_payment = forms.BooleanField(required=True)
        return BankWireForm
        
    def get_payment_template(self) -> str:
        """Return the payment form template path"""
        return "bank_wire_payment/payment_form.html"
        
    def get_template_context(self) -> Dict[str, Any]:
        """Return context data for the payment template"""
        settings = self.get_settings()
        return {
            'bank_details': {
                'bank_name': settings.get('bank_name', 'Sample Bank'),
                'account_holder': settings.get('account_holder', 'Sample Account Holder'),
                'account_number': settings.get('account_number', '1234567890'),
                'iban': settings.get('iban', 'PL12345678901234567890123456'),
                'swift_code': settings.get('swift_code', 'SAMPLEBANK'),
                'additional_info': settings.get('additional_info', 'Please include your order reference in the payment description.')
            }
        }
        
    def process_payment(self, request: HttpRequest, form_data: Dict) -> Dict[str, Any]:
        """Process payment and return result"""
        try:
            # Generate unique reference number
            reference = f"BW-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            # Get module settings
            settings = self.get_settings()
            
            # Create payment record
            payment_data = {
                'reference': reference,
                'status': 'pending',
                'payment_method': 'bank_wire',
                'created_at': datetime.now(),
                'bank_details': {
                    'bank_name': settings.get('bank_name', ''),
                    'account_number': settings.get('account_number', ''),
                    'account_holder': settings.get('account_holder', ''),
                    'swift_code': settings.get('swift_code', ''),
                    'iban': settings.get('iban', ''),
                    'additional_info': settings.get('additional_info', '')
                }
            }
            
            # Store payment data in session for success page
            request.session['bank_wire_payment'] = payment_data
            
            return {
                'success': True,
                'reference': reference,
                'redirect_url': reverse('bank_wire_payment:payment_success')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'redirect_url': reverse('bank_wire_payment:payment_error')
            }
    
    def validate_payment_data(self, form_data: Dict) -> List[str]:
        """Validate payment form data"""
        errors = []
        if not form_data.get('confirm_payment'):
            errors.append("Payment confirmation is required")
        return errors
    
    def get_payment_methods(self):
        """Return available payment methods"""
        return [{
            'id': 'bank_wire',
            'name': 'Bank Wire Transfer',
            'description': 'Pay via bank wire transfer',
            'icon': 'fas fa-university',
            'fee': 0.00
        }]
    
    def get_urls(self) -> List:
        """Get module URL patterns"""
        from django.urls import path
        from . import views
        
        return [
            path('payment_form/', views.payment_form, name='payment_form'),
            path('payment_process/', views.payment_process, name='payment_process'),
            path('payment_success/', views.payment_success, name='payment_success'),
            path('payment_error/', views.payment_error, name='payment_error'),
        ] 