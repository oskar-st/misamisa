// Checkout page functionality

export function initialize() {
    console.log('Checkout page initialized');
    
    // Add checkout-page class to body for styling
    document.body.classList.add('checkout-page');
    
    // Respect the current global theme - don't override it
    // Listen for theme changes to ensure checkout stays in sync
    document.addEventListener('themeChanged', function(event) {
        console.log('Checkout page: Theme changed to', event.detail.theme);
        // The theme is already applied to document.documentElement by the theme toggle
        // No additional action needed - CSS variables will handle the styling
    });
    
    // Move checkout navigation to header inline with logo
    const headerInner = document.querySelector('.site-header .header-inner');
    const template = document.getElementById('checkout-nav-template');
    
    if (headerInner && template) {
        // Clone the checkout navigation
        const checkoutNav = template.querySelector('.checkout-progress').cloneNode(true);
        
        // Add the navigation to header
        headerInner.appendChild(checkoutNav);
        
        console.log('Checkout navigation added to header inline with logo');
    }
    
    // Address selection validation
    const form = document.getElementById('shipping-payment-form');
    if (form && !form.dataset.addressValidationBound) {
        form.dataset.addressValidationBound = 'true';
        
        // Function to get or create error element
        const getOrCreateError = (id, parentSelector, message) => {
            let errorEl = document.getElementById(id);
            if (!errorEl) {
                // Find parent element
                const parent = form.querySelector(parentSelector);
                if (parent) {
                    errorEl = document.createElement('div');
                    errorEl.id = id;
                    errorEl.className = 'error-message';
                    errorEl.style.display = 'none';
                    errorEl.innerHTML = `<span>${message}</span>`;
                    // Insert after the form-row containing the select
                    const formRow = parent.querySelector('.form-row');
                    if (formRow && formRow.parentNode) {
                        formRow.parentNode.insertBefore(errorEl, formRow.nextSibling);
                    } else {
                        parent.appendChild(errorEl);
                    }
                }
            }
            return errorEl;
        };
        
        // Try to get existing error elements from template, or create them
        let shippingError = document.getElementById('shipping-address-error');
        if (!shippingError) {
            shippingError = getOrCreateError(
                'shipping-address-error',
                '.address-selection-section',
                'Wybierz adres dostawy, aby przejść do podsumowania.'
            );
        }
        
        let invoiceError = document.getElementById('invoice-address-error');
        if (!invoiceError) {
            invoiceError = getOrCreateError(
                'invoice-address-error',
                '#company-address-form .address-selection-section',
                'Wybierz dane do faktury, aby przejść do podsumowania.'
            );
        }
        
        const hideErrors = () => {
            if (shippingError) {
                shippingError.style.display = 'none';
            }
            if (invoiceError) {
                invoiceError.style.display = 'none';
            }
        };
        
        form.addEventListener('submit', function(event) {
            hideErrors();
            
            const buyerTypeInput = form.querySelector('input[name="buyer_type"]:checked');
            const buyerType = buyerTypeInput ? buyerTypeInput.value : 'private';
            
            let hasError = false;
            
            if (buyerType === 'private') {
                const addressSelect = form.querySelector('select[name="selected_shipping_address"]');
                if (addressSelect && !addressSelect.value) {
                    hasError = true;
                    if (shippingError) {
                        console.log('Showing shipping address error');
                        shippingError.style.display = 'block';
                        // Force reflow to ensure display change is applied
                        shippingError.offsetHeight;
                        setTimeout(() => {
                            shippingError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }, 50);
                    } else {
                        console.log('Shipping error element not found');
                    }
                }
            } else if (buyerType === 'company') {
                const invoiceSelect = form.querySelector('select[name="selected_invoice_details"]');
                if (invoiceSelect && !invoiceSelect.value) {
                    hasError = true;
                    if (invoiceError) {
                        console.log('Showing invoice address error');
                        invoiceError.style.display = 'block';
                        // Force reflow to ensure display change is applied
                        invoiceError.offsetHeight;
                        setTimeout(() => {
                            invoiceError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }, 50);
                    } else {
                        console.log('Invoice error element not found');
                    }
                }
            }
            
            if (hasError) {
                event.preventDefault();
                console.log('Form submission prevented: address not selected');
            }
        });
        
        // Hide errors when user selects an address
        const shippingSelect = form.querySelector('select[name="selected_shipping_address"]');
        const invoiceSelect = form.querySelector('select[name="selected_invoice_details"]');
        
        if (shippingSelect) {
            shippingSelect.addEventListener('change', () => {
                if (shippingError && shippingSelect.value) {
                    shippingError.style.display = 'none';
                }
            });
        }
        
        if (invoiceSelect) {
            invoiceSelect.addEventListener('change', () => {
                if (invoiceError && invoiceSelect.value) {
                    invoiceError.style.display = 'none';
                }
            });
        }
    }
}

// Only initialize when called by main.js for checkout pages
// No auto-initialization to prevent running on all pages

// Handle HTMX reinitialization
document.addEventListener('htmx:reinitialize-checkout', function() {
    initialize();
});