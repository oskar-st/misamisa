#!/usr/bin/env python3
"""
Utility script to create module ZIP files and place them in the downloads folder.
This ensures consistent and reliable ZIP creation for module distribution.
"""

import os
import zipfile
import shutil
import tempfile
from pathlib import Path
from django.conf import settings
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def create_module_zip(module_name, output_name=None, source_dir=None):
    """
    Create a ZIP file for a module and place it in the downloads folder.
    
    Args:
        module_name (str): Name of the module to package
        output_name (str): Name for the output ZIP file (without .zip extension)
        source_dir (str): Source directory to package (defaults to modules/module_name)
    
    Returns:
        str: Path to the created ZIP file
    """
    # Setup paths
    base_dir = Path(settings.BASE_DIR)
    modules_dir = base_dir / 'modules'
    downloads_dir = base_dir / 'downloads'
    
    # Determine source directory
    if source_dir is None:
        source_dir = modules_dir / module_name
    else:
        source_dir = Path(source_dir)
    
    # Determine output name
    if output_name is None:
        output_name = f"{module_name}_module"
    
    # Ensure downloads directory exists
    downloads_dir.mkdir(exist_ok=True)
    
    # Create temporary directory for ZIP creation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        print(f"Creating ZIP for module: {module_name}")
        print(f"Source directory: {source_dir}")
        print(f"Output name: {output_name}")
        
        # Check if source directory exists
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        
        # Copy module files to temp directory
        temp_module_dir = temp_path / module_name
        if source_dir.is_dir():
            shutil.copytree(source_dir, temp_module_dir)
        else:
            raise ValueError(f"Source directory is not a directory: {source_dir}")
        
        # Create ZIP file
        zip_path = downloads_dir / f"{output_name}.zip"
        
        print(f"Creating ZIP file: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_module_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_name = file_path.relative_to(temp_module_dir)
                    zipf.write(file_path, arc_name)
                    print(f"  Added: {arc_name}")
        
        # Verify ZIP file was created
        if not zip_path.exists():
            raise RuntimeError(f"Failed to create ZIP file: {zip_path}")
        
        # Get file size
        file_size = zip_path.stat().st_size
        print(f"✅ ZIP file created successfully: {zip_path}")
        print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        return str(zip_path)

def create_improved_from_zip(source_zip_name, output_name, improvements=None):
    """
    Create an improved version of a module from an existing ZIP file.
    
    Args:
        source_zip_name (str): Name of the source ZIP file in downloads folder
        output_name (str): Name for the output ZIP file (without .zip extension)
        improvements (dict): Dictionary of file paths to improved content
    
    Returns:
        str: Path to the created ZIP file
    """
    base_dir = Path(settings.BASE_DIR)
    downloads_dir = base_dir / 'downloads'
    
    source_zip_path = downloads_dir / f"{source_zip_name}.zip"
    if not source_zip_path.exists():
        raise FileNotFoundError(f"Source ZIP not found: {source_zip_path}")
    
    print(f"Creating improved version from: {source_zip_name}")
    print(f"Output name: {output_name}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Extract the source ZIP
        print("Extracting source ZIP...")
        with zipfile.ZipFile(source_zip_path, 'r') as zipf:
            zipf.extractall(temp_path)
        
        # Find the actual module directory
        extracted_dir = temp_path
        if (temp_path / 'stripe_payment').exists():
            extracted_dir = temp_path / 'stripe_payment'
        
        # Apply improvements if provided
        if improvements:
            print("Applying improvements...")
            for file_path, content in improvements.items():
                full_path = extracted_dir / file_path
                if full_path.exists():
                    full_path.write_text(content)
                    print(f"  ✅ Updated: {file_path}")
                else:
                    print(f"  ⚠️  File not found: {file_path}")
        
        # Create the improved ZIP
        zip_path = create_module_zip('stripe_payment', output_name, extracted_dir)
        
        print(f"✅ Improved module ZIP created: {zip_path}")
        return zip_path

def get_improved_stripe_payment_form():
    """Get the improved Stripe payment form content."""
    return '''{% load static %}
{% load i18n %}

<div class="stripe-payment-form" id="stripe-payment-form">
    <div class="payment-info">
        <div class="payment-methods-preview">
            <h4>Available Payment Methods:</h4>
            <div class="payment-methods-list">
                <div class="payment-method-badge">
                    <i class="fas fa-credit-card"></i>
                    <span>Credit/Debit Cards</span>
                </div>
                <div class="payment-method-badge">
                    <i class="fas fa-university"></i>
                    <span>Przelewy24</span>
                </div>
                <div class="payment-method-badge">
                    <i class="fas fa-mobile-alt"></i>
                    <span>BLIK</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Stripe Payment Element will be inserted here -->
    <div id="stripe-payment-element" class="stripe-payment-element">
        <div class="loading-message">
            <i class="fas fa-spinner fa-spin"></i>
            <span>Loading payment form...</span>
        </div>
    </div>

    <div class="payment-security">
        <div class="security-info">
            <i class="fas fa-shield-alt"></i>
            <span>256-bit SSL encryption</span>
        </div>
        <div class="security-info">
            <i class="fab fa-stripe"></i>
            <span>Powered by Stripe</span>
        </div>
    </div>
</div>

<style>
.stripe-payment-form {
    padding: 20px;
    background: #fff;
    border-radius: 8px;
    border: 1px solid #e9ecef;
}

.payment-info {
    margin-bottom: 20px;
}

.payment-methods-preview h4 {
    margin: 0 0 15px 0;
    color: #333;
    font-size: 16px;
    font-weight: 600;
}

.payment-methods-list {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.payment-method-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    font-size: 14px;
    color: #495057;
}

.payment-method-badge i {
    color: #6772e5;
    font-size: 16px;
}

.stripe-payment-element {
    margin: 20px 0;
    min-height: 200px;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f8f9fa;
}

.loading-message {
    text-align: center;
    color: #6c757d;
}

.loading-message i {
    font-size: 24px;
    margin-bottom: 10px;
    display: block;
    color: #6772e5;
}

.payment-security {
    margin-top: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 6px;
    display: flex;
    justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
}

.security-info {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #6c757d;
    font-size: 14px;
}

.security-info i {
    color: #28a745;
}

/* Error message styling */
.error-message {
    color: #dc3545;
    text-align: center;
    padding: 20px;
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 6px;
}

/* Responsive design */
@media (max-width: 768px) {
    .payment-methods-list {
        flex-direction: column;
        gap: 10px;
    }
    
    .payment-security {
        flex-direction: column;
        gap: 10px;
        text-align: center;
    }
}
</style>

<script src="https://js.stripe.com/v3/"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const stripePublicKey = '{{ stripe_public_key }}';
    const stripe = Stripe(stripePublicKey, {
        betas: ['p24_pm_beta_1', 'blik_pm_beta_1']
    });
    
    let elements;
    let paymentElement;
    let isInitialized = false;
    
    // Initialize Stripe payment form
    async function initializeStripePayment() {
        if (isInitialized) return;
        
        try {
            const orderData = {
                amount: parseFloat('{{ total|default:0 }}'),
                currency: 'pln'
            };
            
            if (!orderData.amount || orderData.amount <= 0) {
                throw new Error('Invalid order total');
            }
            
            // Create payment intent
            const response = await fetch('/modules/stripe_payment/create-payment-intent/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(orderData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Create Elements
                elements = stripe.elements({
                    clientSecret: result.client_secret,
                    appearance: {
                        theme: 'stripe',
                        variables: {
                            colorPrimary: '#6772e5',
                            colorBackground: '#ffffff',
                            colorText: '#30313d',
                            colorDanger: '#df1b41',
                            fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                            spacingUnit: '4px',
                            borderRadius: '8px'
                        }
                    }
                });
                
                // Create payment element
                paymentElement = elements.create('payment', {
                    layout: {
                        type: 'tabs',
                        defaultCollapsed: false,
                        spacedAccordionItems: false
                    },
                    paymentMethodOrder: ['card', 'p24', 'blik']
                });
                
                // Mount the payment element
                paymentElement.mount('#stripe-payment-element');
                
                isInitialized = true;
                
            } else {
                throw new Error(result.error || 'Failed to create payment intent');
            }
            
        } catch (error) {
            console.error('Error initializing Stripe payment:', error);
            document.getElementById('stripe-payment-element').innerHTML = 
                '<div class="error-message">Error loading payment form. Please refresh the page.</div>';
        }
    }
    
    // Initialize when this payment method is selected
    const stripeRadio = document.querySelector('input[value="stripe_payment"]');
    if (stripeRadio) {
        stripeRadio.addEventListener('change', function() {
            if (this.checked) {
                initializeStripePayment();
            }
        });
        
        // If Stripe is already selected, initialize immediately
        if (stripeRadio.checked) {
            initializeStripePayment();
        }
    }
    
    // Override the checkout form submission to handle Stripe payments
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', async function(event) {
            const selectedPaymentMethod = document.querySelector('input[name="payment_method"]:checked');
            
            if (selectedPaymentMethod && selectedPaymentMethod.value === 'stripe_payment') {
                event.preventDefault();
                
                if (!elements || !isInitialized) {
                    alert('Payment form not loaded. Please wait a moment and try again.');
                    return;
                }
                
                const submitButton = document.querySelector('.checkout-btn');
                const originalText = submitButton.innerHTML;
                
                // Disable submit button
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing Payment...';
                
                try {
                    // Confirm payment
                    const {error} = await stripe.confirmPayment({
                        elements: elements,
                        confirmParams: {
                            return_url: window.location.origin + '/checkout/success/'
                        }
                    });
                    
                    if (error) {
                        let errorMessage = 'Payment failed. ';
                        if (error.type === 'card_error' || error.type === 'validation_error') {
                            errorMessage += error.message;
                        } else {
                            errorMessage += 'An unexpected error occurred.';
                        }
                        
                        alert(errorMessage);
                        submitButton.disabled = false;
                        submitButton.innerHTML = originalText;
                    }
                    // Payment succeeded - user will be redirected to success page
                    
                } catch (error) {
                    console.error('Payment error:', error);
                    alert('An error occurred during payment. Please try again.');
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }
            }
        });
    }
});
</script>'''

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'create':
            if len(sys.argv) < 3:
                print("Usage: python create_module_zip.py create <module_name> [output_name]")
                sys.exit(1)
            
            module_name = sys.argv[2]
            output_name = sys.argv[3] if len(sys.argv) > 3 else None
            
            create_module_zip(module_name, output_name)
            
        elif command == 'improve-stripe':
            if len(sys.argv) < 3:
                print("Usage: python create_module_zip.py improve-stripe <source_zip_name> [output_name]")
                print("Example: python create_module_zip.py improve-stripe stripe_payment_module_clean_core stripe_payment_module_improved_v2")
                sys.exit(1)
            
            source_zip = sys.argv[2]
            output_name = sys.argv[3] if len(sys.argv) > 3 else 'stripe_payment_module_improved_v2'
            
            improvements = {
                'templates/stripe_payment/payment_form.html': get_improved_stripe_payment_form()
            }
            
            create_improved_from_zip(source_zip, output_name, improvements)
            
        else:
            print("Unknown command. Available commands:")
            print("  create <module>  - Create ZIP for specified module")
            print("  improve-stripe <source> [output] - Create improved Stripe module from source ZIP")
    else:
        print("Usage: python create_module_zip.py <command>")
        print("Commands:")
        print("  create <module>  - Create ZIP for specified module")
        print("  improve-stripe <source> [output] - Create improved Stripe module from source ZIP") 