"""
Stripe Payment Module with Multiple Payment Methods Support
"""
import os
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path
from modules.base import PaymentModuleBase
from .forms import StripePaymentForm


class StripeModule(PaymentModuleBase):
    """Stripe payment gateway module with support for multiple payment methods."""
    
    name = "stripe"
    display_name = "Stripe"
    description = "Accept payments via Stripe (Cards, Przelewy24, BLIK)"
    version = "1.0.0"
    author = "System Admin"
    category = "payment"
    color = "#6772e5"  # Stripe brand color
    icon = "fab fa-stripe"  # FontAwesome Stripe icon
    
    # Supported payment methods
    supported_payment_methods = [
        "card",      # Visa, Mastercard, etc.
        "p24",       # Przelewy24 bank payments
        "blik",      # BLIK real-time payments
    ]
    
    def __init__(self, module_name="stripe_payment", module_path=None):
        if module_path is None:
            import os
            module_path = os.path.dirname(os.path.abspath(__file__))
        super().__init__(module_name, module_path)
        # Stripe API key will be initialized when needed
    
    def _init_stripe(self):
        """Initialize Stripe with secret key when needed."""
        try:
            import stripe
            # Try to get configuration from saved file
            config = self._get_config()
            if config and config.get('stripe_secret_key'):
                stripe.api_key = config['stripe_secret_key']
                return stripe
            # Fallback to Django settings
            elif hasattr(settings, 'STRIPE_SECRET_KEY') and settings.STRIPE_SECRET_KEY:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                return stripe
            else:
                raise ValueError("Stripe secret key not configured")
        except ImportError:
            raise ImportError("Stripe package is not installed. Please install it first.")
    
    def _get_config(self):
        """Get module configuration from saved file."""
        try:
            config_file = os.path.join(settings.BASE_DIR, 'modules', 'config', 'stripe_payment_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading Stripe config: {e}")
        return None
    
    def get_stripe_public_key(self):
        """Get Stripe public key from configuration."""
        # First try to get from environment variables (highest priority)
        env_key = os.getenv('STRIPE_PUBLIC_KEY')
        if env_key:
            return env_key
        
        # Then try to get from saved config file
        config = self._get_config()
        if config and config.get('stripe_public_key'):
            return config['stripe_public_key']
        
        # Fallback to Django settings
        return getattr(settings, 'STRIPE_PUBLIC_KEY', 'pk_test_your_test_key_here')
    
    def install(self):
        """Install the module."""
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                # Create any custom tables if needed
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stripe_transactions (
                        id SERIAL PRIMARY KEY,
                        order_id VARCHAR(255) NOT NULL,
                        stripe_payment_intent_id VARCHAR(255) NOT NULL,
                        amount INTEGER NOT NULL,
                        currency VARCHAR(3) DEFAULT 'pln',
                        status VARCHAR(50) NOT NULL,
                        payment_method VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            
            return True, "Stripe module installed successfully"
        except Exception as e:
            return False, f"Failed to install Stripe module: {str(e)}"
    
    def uninstall(self):
        """Uninstall the module."""
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                # Drop custom tables
                cursor.execute("DROP TABLE IF EXISTS stripe_transactions")
            
            return True, "Stripe module uninstalled successfully"
        except Exception as e:
            return False, f"Failed to uninstall Stripe module: {str(e)}"
    
    def enable(self):
        """Enable the module."""
        try:
            # Set module as enabled in database or settings
            self.is_enabled = True
            return True, "Stripe module enabled successfully"
        except Exception as e:
            return False, f"Failed to enable Stripe module: {str(e)}"
    
    def disable(self):
        """Disable the module."""
        try:
            # Set module as disabled in database or settings
            self.is_enabled = False
            return True, "Stripe module disabled successfully"
        except Exception as e:
            return False, f"Failed to disable Stripe module: {str(e)}"
    
    def get_payment_form(self):
        """Get the payment form class."""
        return StripePaymentForm
    
    def get_payment_template(self):
        """Get the payment form template path."""
        return "stripe_payment/templates/stripe_payment/payment_form.html"
    
    def get_admin_config_template(self):
        """Get the admin configuration template."""
        return "stripe_payment/admin/config.html"
    
    def create_payment_intent(self, request):
        """Create a payment intent with multiple payment method support."""
        try:
            import json
            
            # Parse request data
            data = json.loads(request.body)
            amount = data.get('amount', 0)
            currency = data.get('currency', 'pln')
            email = data.get('email', '')
            
            # Validate amount
            if not amount or amount <= 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid amount'
                })
            
            # Initialize Stripe
            stripe_instance = self._init_stripe()
            
            # Create payment intent with multiple payment methods
            payment_intent = stripe_instance.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                metadata={
                    'customer_email': email,
                    'order_type': 'cookies_website'
                },
                automatic_payment_methods={
                    'enabled': True,
                }
            )
            
            return JsonResponse({
                'success': True,
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    def process_payment(self, request, form_data):
        """Process payment through Stripe with multiple payment methods."""
        try:
            # Get order from request or form_data
            order = form_data.get('order')
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found'
                }
            
            # Initialize Stripe
            stripe_instance = self._init_stripe()
            
            # Create payment intent with multiple payment methods
            payment_intent = stripe_instance.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency='pln',
                metadata={
                    'order_id': str(order.id),
                    'customer_email': form_data.get('email', ''),
                    'order_type': 'cookies_website'
                },
                # Enable automatic payment methods (this will automatically detect card, p24, blik)
                automatic_payment_methods={
                    'enabled': True,
                }
            )
            
            # Store transaction record
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO stripe_transactions 
                    (order_id, stripe_payment_intent_id, amount, status, payment_method)
                    VALUES (%s, %s, %s, %s, %s)
                """, [
                    str(order.id),
                    payment_intent.id,
                    int(order.total_amount * 100),
                    'pending',
                    'multiple_methods'
                ])
            
            return {
                'success': True,
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_payment_data(self, form_data):
        """Validate payment form data."""
        errors = []
        
        if not form_data.get('email'):
            errors.append('Email is required')
        
        # For embedded checkout, we don't need to validate payment method
        # as Stripe handles the payment method selection
        
        return errors
    
    def get_urls(self):
        """Get module URLs."""
        from django.urls import path
        return [
            path('webhook/', self.stripe_webhook, name='stripe_webhook'),
            path('create-payment-intent/', self.create_payment_intent, name='create_payment_intent'),
        ]
    
    @csrf_exempt
    @require_http_methods(["POST"])
    def stripe_webhook(self, request):
        """Handle Stripe webhook events."""
        try:
            payload = request.body
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
            
            # Verify webhook signature
            stripe_instance = self._init_stripe()
            event = stripe_instance.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            # Handle the event
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                self.handle_payment_success(payment_intent)
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                self.handle_payment_failure(payment_intent)
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def handle_payment_success(self, payment_intent):
        """Handle successful payment."""
        try:
            # Update transaction status
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE stripe_transactions 
                    SET status = 'succeeded', payment_method = %s
                    WHERE stripe_payment_intent_id = %s
                """, [
                    payment_intent.payment_method_types[0] if payment_intent.payment_method_types else 'unknown',
                    payment_intent.id
                ])
            
            print(f"Payment succeeded: {payment_intent.id}")
            
        except Exception as e:
            print(f"Error handling payment success: {e}")
    
    def handle_payment_failure(self, payment_intent):
        """Handle failed payment."""
        try:
            # Update transaction status
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE stripe_transactions 
                    SET status = 'failed'
                    WHERE stripe_payment_intent_id = %s
                """, [payment_intent.id])
            
            print(f"Payment failed: {payment_intent.id}")
            
        except Exception as e:
            print(f"Error handling payment failure: {e}")
    
    def get_payment_methods_info(self):
        """Get information about supported payment methods."""
        return {
            'card': {
                'name': 'Credit/Debit Cards',
                'description': 'Visa, Mastercard, and other major cards',
                'icon': 'fas fa-credit-card',
                'color': '#1a1a1a'
            },
            'p24': {
                'name': 'Przelewy24',
                'description': 'Pay with your bank account',
                'icon': 'fas fa-university',
                'color': '#ff6b35'
            },
            'blik': {
                'name': 'BLIK',
                'description': 'Real-time mobile payments',
                'icon': 'fas fa-mobile-alt',
                'color': '#0066cc'
            }
        }


# Module instance
module = StripeModule() 