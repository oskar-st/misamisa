from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from .models import Category, Product
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from shop.models import ShippingMethod, PaymentMethod, Order, OrderItem
from accounts.models import Address, CustomUser
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
from modules.manager import module_manager
from django.conf import settings
from .cart_utils import save_cart_to_database, validate_and_clean_cart, get_cart_change_messages
from .forms import CheckoutShippingPaymentForm, OrderSummaryForm


def get_cart_items(request):
    """Get cart items from session."""
    cart = request.session.get('cart', {})
    product_ids = list(cart.keys())
    products = Product.objects.filter(id__in=product_ids, is_active=True)
    cart_items = []
    
    for product in products:
        qty = cart.get(str(product.id), 0)
        price = product.discount_price or product.price
        subtotal = price * qty
        cart_items.append({
            'product': product,
            'quantity': qty,
            'price': price,
            'subtotal': subtotal,
        })
    
    return cart_items


def clear_cart(request):
    """Clear the cart from session."""
    request.session['cart'] = {}


def product_list(request):
    """Display all active products (admin view)"""
    products = Product.objects.filter(is_active=True).select_related('category')
    context = {
        'products': products,
        'title': _('All Products')
    }
    return render(request, 'shop/product_list.html', context)

def category_detail(request, slug):
    """Display products in a specific category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    descendant_categories = category.get_descendants(include_self=True)
    products = Product.objects.filter(
        category__in=descendant_categories,
        is_active=True
    ).select_related('category')
    
    # Get hierarchical categories for sidebar
    sidebar_categories = Category.objects.filter(parent=None, is_active=True).prefetch_related(
        'children__children__children__children__children'  # Prefetch up to 6 levels for unlimited nesting
    ).order_by('name')
    
    context = {
        'category': category,
        'products': products,
        'title': category.name,
        'sidebar_categories': sidebar_categories,
    }
    
    # For htmx requests, return just the main content
    if request.headers.get('HX-Request'):
        return render(request, 'shop/product_list_content.html', context)
    
    return render(request, 'shop/category_detail.html', context)

def product_detail(request, slug):
    """Display a specific product (admin view)"""
    # This function is removed as per the instructions
    pass

# --- PUBLIC VIEWS ---
def product_list_public(request, category_slug=None):
    """Display all products, with optional category filtering"""
    
    # Optimize category query - only fetch what we need
    categories = Category.objects.filter(is_active=True).values('id', 'name', 'slug').order_by('name')
    category = None
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related(
        'images'  # Prefetch product images
    )
    
    # Handle category filtering - first check parameter, then GET request
    if not category_slug:
        category_slug = request.GET.get('category')
    
    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug, is_active=True)
            descendant_categories = category.get_descendants(include_self=True)
            products = products.filter(category__in=descendant_categories)
        except Category.DoesNotExist:
            pass

    # Pagination - keep at 12 products per page
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Generate breadcrumbs
    breadcrumbs = [{'title': 'Misamisa', 'url': reverse('home')}]
    
    # Determine title
    if category:
        title = category.name
        breadcrumbs.append({'title': _('Shop'), 'url': reverse('shop:public_product_list')})
        breadcrumbs.append({'title': category.name, 'url': reverse('category_or_product', kwargs={'slug': category.slug})})
    else:
        title = _('All Products')
        breadcrumbs.append({'title': _('Shop'), 'url': reverse('shop:public_product_list')})

    # Optimize sidebar categories - only fetch what's needed for display
    sidebar_categories = Category.objects.filter(parent=None, is_active=True).prefetch_related(
        Prefetch('children', queryset=Category.objects.filter(is_active=True).prefetch_related(
            Prefetch('children', queryset=Category.objects.filter(is_active=True))
        ))
    ).order_by('name')[:10]  # Limit to first 10 top-level categories
    
    # Get view preference from headers (preferred), URL parameter (fallback), then default to 'grid'
    current_view = request.headers.get('X-View-Preference') or request.GET.get('view', 'grid')
    
    context = {
        'categories': categories,
        'category': category,
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'title': title,
        'breadcrumbs': breadcrumbs,
        'sidebar_categories': sidebar_categories,
        'current_view': current_view,  # Add current view to context
    }
    
    # For htmx requests, return appropriate content
    if request.headers.get('HX-Request'):
        # Check HTMX target to determine what template to return
        hx_target = request.headers.get('X-HX-Target', '')
        
        # HTMX request handling
        
        if hx_target == '#main-content':
            # Top menu navigation - return full shop layout without base template
            return render(request, 'shop/product_list_content.html', context)
        else:
            # Sidebar navigation - return just the product list container
            return render(request, 'shop/product_list_container.html', context)
    
    return render(request, 'shop/product_list.html', context)

def product_detail_public(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Generate breadcrumbs
    breadcrumbs = [{'title': 'Misamisa', 'url': reverse('home')}]
    # Add full category parent chain
    parent_chain = []
    current = product.category
    while current.parent:
        parent_chain.append(current.parent)
        current = current.parent
    for parent in reversed(parent_chain):
        breadcrumbs.append({'title': parent.name, 'url': reverse('category_or_product', kwargs={'slug': parent.slug})})
    breadcrumbs.append({'title': product.category.name, 'url': reverse('category_or_product', kwargs={'slug': product.category.slug})})
    breadcrumbs.append({'title': product.name, 'url': product.get_absolute_url()})
    
    context = {
        'product': product,
        'title': product.name,
        'breadcrumbs': breadcrumbs,
    }
    
    # For htmx requests, create a minimal content template
    if request.headers.get('HX-Request'):
        print(f"HTMX request detected for product: {request.path}")
        return render(request, 'shop/product_detail_content.html', context)
    
    return render(request, 'shop/product_detail_enhanced.html', context)

def cart_view(request):
    # Cart is stored in session as {product_id: quantity}
    cart = request.session.get('cart', {})
    message = None
    
    # Validate cart and get any change messages
    cart_change_messages = get_cart_change_messages(request)
    
    # Handle add, update, remove
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action', 'add')
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except (Product.DoesNotExist, ValueError, TypeError):
            product = None
        if product:
            # Convert product_id to string for consistency
            product_id_str = str(product_id)
            if action == 'add':
                qty = int(request.POST.get('quantity', 1))
                # Validate quantity against stock
                if qty > product.stock:
                    qty = product.stock
                    message = _('Quantity adjusted to available stock.')
                
                if product_id_str in cart:
                    new_qty = cart[product_id_str] + qty
                    if new_qty > product.stock:
                        cart[product_id_str] = product.stock
                        message = _('Maximum stock reached.')
                    else:
                        cart[product_id_str] = new_qty
                        message = _('Added to cart.')
                else:
                    cart[product_id_str] = qty
                    message = _('Added to cart.')
            elif action == 'update':
                qty = int(request.POST.get('quantity', 1))
                if qty > 0:
                    # Validate quantity against stock
                    if qty > product.stock:
                        qty = product.stock
                        message = _('Quantity adjusted to available stock.')
                    cart[product_id_str] = qty
                    message = message or _('Cart updated.')
                else:
                    cart.pop(product_id_str, None)
                    message = _('Item removed.')
            elif action == 'remove':
                cart.pop(product_id_str, None)
                message = _('Item removed.')
        
        # Validate entire cart after changes
        if request.user.is_authenticated:
            cart, changes_made, change_messages = validate_and_clean_cart(request.user, cart)
            if change_messages:
                cart_change_messages.extend(change_messages)
        
        request.session['cart'] = cart
        
        # Sync cart to database for authenticated users
        if request.user.is_authenticated:
            save_cart_to_database(request.user, cart)
        
        return HttpResponseRedirect(reverse('cart_view'))
    
    # Validate cart on load for all users (but safely)
    if cart:
        try:
            cart, changes_made, change_messages = validate_and_clean_cart(request.user, cart)
            if changes_made:
                request.session['cart'] = cart
                # Save to database only for authenticated users
                if request.user.is_authenticated:
                    save_cart_to_database(request.user, cart)
                if change_messages:
                    cart_change_messages.extend(change_messages)
        except Exception as e:
            # If validation fails, log the error but don't crash
            print(f"Cart validation error: {e}")
            # Keep the original cart if validation fails
            pass
    
    # Prepare cart items for display
    product_ids = list(cart.keys())
    products = Product.objects.filter(id__in=product_ids, is_active=True)
    cart_items = []
    total = 0
    for product in products:
        qty = cart.get(str(product.id), 0)
        price = product.discount_price or product.price
        subtotal = price * qty
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': qty,
            'price': price,
            'subtotal': subtotal,
        })
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'message': message,
        'cart_change_messages': cart_change_messages,
        'title': _('Cart'),
    }
    
    # For htmx requests, return just the main content
    if request.headers.get('HX-Request'):
        return render(request, 'shop/cart_content.html', context)
    
    return render(request, 'shop/cart.html', context)

def checkout(request):
    """Checkout view with modular payment methods."""
    cart_items = get_cart_items(request)
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_view')
    
    total = sum(item['subtotal'] for item in cart_items)
    
    # Get available payment modules
    payment_modules = module_manager.get_payment_modules()
    
    # Prepare payment methods for template
    payment_methods = []
    
    for module_name, module in payment_modules.items():
        if module.is_installed and module.is_enabled:
            payment_form = module.get_payment_form()
            
            # Get payment method info from module
            payment_info = {
                'code': module_name,
                'name': getattr(module, 'display_name', module_name.title()),
                'description': getattr(module, 'description', 'Payment via ' + module_name.title()),
                'color': getattr(module, 'color', '#007bff'),  # Default blue color
                'icon': getattr(module, 'icon', 'fas fa-credit-card'),  # Default icon
            }
            
            # Get module-specific configuration if available
            module_config = {}
            if hasattr(module, 'get_public_config'):
                module_config = module.get_public_config()
            
            # Get template context from module if available
            template_context = {}
            if hasattr(module, 'get_template_context'):
                template_context = module.get_template_context()
            
            payment_methods.append({
                'module_name': module_name,
                'module': module,
                'info': payment_info,
                'form': payment_form() if payment_form else None,
                'template_path': module.get_payment_template(),
                'config': module_config,
                'template_context': template_context,
            })
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'payment_methods': payment_methods,
    }
    
    # Add Stripe configuration if Stripe module is available
    stripe_module = payment_modules.get('stripe_payment')
    if stripe_module and stripe_module.is_installed and stripe_module.is_enabled:
        try:
            stripe_public_key = stripe_module.get_stripe_public_key()
            context['stripe_public_key'] = stripe_public_key
        except Exception as e:
            print(f"Error getting Stripe public key: {e}")
            context['stripe_public_key'] = 'pk_test_your_test_key_here'
    
    # For htmx requests, return just the main content
    if request.headers.get('HX-Request'):
        return render(request, 'shop/checkout_content.html', context)
    
    return render(request, 'shop/checkout.html', context)

@login_required
def checkout_step2_shipping_payment(request):
    """Step 2: Shipping & Payment."""
    cart_items = get_cart_items(request)
    if not cart_items:
        messages.error(request, _('Your cart is empty.'))
        return redirect('cart_view')

    subtotal = sum(item['subtotal'] for item in cart_items)

    if request.method == 'POST':
        form = CheckoutShippingPaymentForm(request.POST, user=request.user)
        if form.is_valid():
            data = {
                'shipping_method_id': form.cleaned_data['shipping_method'].id,
                'buyer_type': form.cleaned_data['buyer_type'],
                'payment_method': form.cleaned_data['payment_method'],
            }
            if data['buyer_type'] == 'private':
                # Handle address selection for private buyers
                selected_address = form.cleaned_data.get('selected_shipping_address')
                
                if selected_address:
                    # Use selected saved address
                    data.update({
                        'shipping_full_name': selected_address.full_name,
                        'shipping_street': selected_address.street,
                        'shipping_postal_code': selected_address.postal_code,
                        'shipping_city': selected_address.city,
                        'shipping_phone': selected_address.phone,
                        'shipping_email': selected_address.email,
                        'selected_shipping_address_id': selected_address.id,
                    })
                else:
                    # Use manually entered address (only available when no saved addresses)
                    data.update({
                        'shipping_full_name': form.cleaned_data['shipping_full_name'],
                        'shipping_street': form.cleaned_data['shipping_street'],
                        'shipping_postal_code': form.cleaned_data['shipping_postal_code'],
                        'shipping_city': form.cleaned_data['shipping_city'],
                        'shipping_phone': form.cleaned_data['shipping_phone'],
                        'shipping_email': form.cleaned_data['shipping_email'],
                    })
            else:
                # Handle invoice details selection for company buyers
                selected_invoice = form.cleaned_data.get('selected_invoice_details')
                
                if selected_invoice:
                    # Use selected saved invoice details
                    data.update({
                        'invoice_vat_id': selected_invoice.vat_id or '',
                        'invoice_company_name': selected_invoice.full_name_or_company,
                        'invoice_street': selected_invoice.street,
                        'invoice_postal_code': selected_invoice.postal_code,
                        'invoice_city': selected_invoice.city,
                        'selected_invoice_details_id': selected_invoice.id,
                    })
                else:
                    # Use manually entered invoice details
                    data.update({
                        'invoice_vat_id': form.cleaned_data.get('invoice_vat_id', ''),
                        'invoice_company_name': form.cleaned_data['invoice_company_name'],
                        'invoice_street': form.cleaned_data['invoice_street'],
                        'invoice_postal_code': form.cleaned_data['invoice_postal_code'],
                        'invoice_city': form.cleaned_data['invoice_city'],
                    })
                
                delivery_same = form.cleaned_data.get('delivery_same_as_invoice', True)
                data['delivery_same_as_invoice'] = delivery_same
                
                # Handle delivery address for companies
                if not delivery_same:
                    selected_delivery = form.cleaned_data.get('selected_delivery_address')
                    if selected_delivery:
                        # Use selected shipping address for delivery
                        data.update({
                            'delivery_full_name': selected_delivery.full_name,
                            'delivery_street': selected_delivery.street,
                            'delivery_postal_code': selected_delivery.postal_code,
                            'delivery_city': selected_delivery.city,
                            'delivery_phone': selected_delivery.phone,
                            'delivery_email': selected_delivery.email,
                            'selected_delivery_address_id': selected_delivery.id,
                        })
                    else:
                        # Use manually entered delivery address
                        data.update({
                            'delivery_full_name': form.cleaned_data['delivery_full_name'],
                            'delivery_street': form.cleaned_data['delivery_street'],
                            'delivery_postal_code': form.cleaned_data['delivery_postal_code'],
                            'delivery_city': form.cleaned_data['delivery_city'],
                            'delivery_phone': form.cleaned_data['delivery_phone'],
                            'delivery_email': form.cleaned_data['delivery_email'],
                        })
            request.session['checkout_data'] = data
            return redirect('checkout_step3_summary')
    else:
        form = CheckoutShippingPaymentForm(user=request.user)

    payment_methods = []
    for module_name, module in module_manager.get_payment_modules().items():
        if module.is_installed and module.is_enabled:
            payment_methods.append({
                'code': module_name,
                'name': getattr(module, 'display_name', module_name.title()),
                'description': getattr(module, 'description', ''),
                'color': getattr(module, 'color', '#007bff'),
                'icon': getattr(module, 'icon', 'fas fa-credit-card'),
            })

    # Get user's saved addresses for template context
    shipping_addresses_count = 0
    invoice_details_count = 0
    if request.user.is_authenticated:
        from accounts.models import ShippingAddress, InvoiceDetails
        shipping_addresses_count = ShippingAddress.objects.filter(user=request.user).count()
        invoice_details_count = InvoiceDetails.objects.filter(user=request.user).count()

    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'payment_methods': payment_methods,
        'shipping_addresses_count': shipping_addresses_count,
        'invoice_details_count': invoice_details_count,
        'step': 2,
    }
    return render(request, 'shop/checkout_step2.html', context)

@login_required
def checkout_step3_summary(request):
    """Step 3: Order Summary."""
    checkout_data = request.session.get('checkout_data')
    if not checkout_data:
        messages.error(request, _('Missing checkout data.'))
        return redirect('checkout_step2_shipping_payment')

    cart_items = get_cart_items(request)
    if not cart_items:
        messages.error(request, _('Your cart is empty.'))
        return redirect('cart_view')

    shipping_method = get_object_or_404(ShippingMethod, id=checkout_data['shipping_method_id'])
    subtotal = sum(item['subtotal'] for item in cart_items)
    shipping_cost = shipping_method.price
    total = subtotal + shipping_cost

    payment_modules = module_manager.get_payment_modules()
    pm_code = checkout_data['payment_method']
    payment_module = payment_modules.get(pm_code)
    payment_method_name = getattr(payment_module, 'display_name', pm_code.title()) if payment_module else pm_code

    summary_form = OrderSummaryForm(request.POST or None)
    if request.method == 'POST' and summary_form.is_valid():
        # Send required fields to place_order
        request.POST = request.POST.copy()
        request.POST['payment_method'] = pm_code
        request.POST['customer_name'] = request.user.get_full_name() or request.user.email
        request.POST['customer_email'] = request.user.email
        return place_order(request)

    context = {
        'checkout_data': checkout_data,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_method': shipping_method,
        'shipping_cost': shipping_cost,
        'total': total,
        'payment_method_name': payment_method_name,
        'summary_form': summary_form,
        'step': 3,
    }
    return render(request, 'shop/checkout_step3.html', context)
def place_order(request):
    """Simple order placement with modular payment processing."""
    if request.method == 'POST':
        # Get cart items
        cart_items = get_cart_items(request)
        if not cart_items:
            messages.error(request, 'Your cart is empty.')
            return redirect('cart_view')
        
        # Calculate total
        total = sum(item['subtotal'] for item in cart_items)
        
        # Get customer information
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        
        if not customer_name or not customer_email:
            messages.error(request, 'Please provide your name and email address.')
            return redirect('checkout_step2_shipping_payment')
        
        # Get selected payment method
        payment_method_code = request.POST.get('payment_method')
        if not payment_method_code:
            messages.error(request, 'Please select a payment method.')
            return redirect('checkout_step2_shipping_payment')
        
        # Get payment module
        payment_modules = module_manager.get_payment_modules()
        payment_module = payment_modules.get(payment_method_code)
        
        if not payment_module:
            messages.error(request, 'Selected payment method is not available.')
            return redirect('checkout_step2_shipping_payment')
        
        # Prepare payment data with customer information
        payment_data = {
            'customer_name': customer_name,
            'customer_email': customer_email,
            'amount': total,
            'currency': 'pln'
        }
        
        # Validate payment data
        if payment_module.get_payment_form():
            form = payment_module.get_payment_form()(request.POST)
            if not form.is_valid():
                messages.error(request, 'Please correct the payment information.')
                return redirect('checkout_step2_shipping_payment')
            payment_data.update(form.cleaned_data)
        
        # Validate payment data with module
        validation_errors = payment_module.validate_payment_data(payment_data)
        if validation_errors:
            for error in validation_errors:
                messages.error(request, error)
            return redirect('checkout_step2_shipping_payment')
        
        # Process payment
        payment_result = payment_module.process_payment(request, payment_data)
        
        if not payment_result.get('success'):
            messages.error(request, payment_result.get('message', 'Payment processing failed.'))
            return redirect('checkout_step2_shipping_payment')
        
        # Create order with customer information
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            shipping_address=None,  # No address for now
            billing_address=None,   # No address for now
            status='pending',
            payment_method_name=payment_method_code,
            payment_transaction_id=payment_result.get('transaction_id'),
            payment_status=payment_result.get('status', 'pending'),
            total_amount=total,
            customer_name=customer_name,
            customer_email=customer_email,
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
        
        # Clear cart
        clear_cart(request)
        
        # Show success message
        messages.success(request, payment_result.get('message', 'Order placed successfully!'))
        
        # Redirect to success page
        return redirect('order_success', order_id=order.id)
    
    return redirect('checkout_step2_shipping_payment')

def order_success(request, order_id=None):
    """Order success page view."""
    # Handle Stripe redirect with payment intent
    payment_intent = request.GET.get('payment_intent')
    redirect_status = request.GET.get('redirect_status')
    
    if payment_intent and redirect_status == 'succeeded':
        # This is a Stripe success redirect
        try:
            # Try to find order by payment intent ID
            order = Order.objects.filter(payment_transaction_id=payment_intent).first()
            if order:
                context = {
                    'order': order,
                    'order_items': order.orderitem_set.all(),
                    'payment_intent': payment_intent,
                    'payment_status': 'succeeded'
                }
            else:
                context = {
                    'order': None,
                    'order_items': [],
                    'payment_intent': payment_intent,
                    'payment_status': 'succeeded',
                    'message': 'Payment completed successfully!'
                }
            # Clear cart after successful Stripe payment
            clear_cart(request)
        except Exception as e:
            context = {
                'order': None,
                'order_items': [],
                'payment_intent': payment_intent,
                'payment_status': 'succeeded',
                'message': 'Payment completed successfully!'
            }
            clear_cart(request)
    else:
        # Handle regular order success with order_id
        if not order_id:
            messages.error(request, 'Order not found.')
            return redirect('home')
        
        try:
            order = Order.objects.get(id=order_id)
            context = {
                'order': order,
                'order_items': order.orderitem_set.all(),
            }
            # Clear cart after successful order
            clear_cart(request)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
            return redirect('home')
    
    return render(request, 'shop/order_success.html', context)

@require_POST
@csrf_exempt
def update_cart_ajax(request):
    """AJAX endpoint for updating cart quantities"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        action = data.get('action', 'update')
        
        # Convert product_id to string for consistency
        product_id_str = str(product_id)
        
        cart = request.session.get('cart', {})
        
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except (Product.DoesNotExist, ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Product not found'}, status=400)
        
        if action == 'update':
            if quantity > 0:
                # Validate quantity against stock
                if quantity > product.stock:
                    quantity = product.stock
                cart[product_id_str] = quantity
            else:
                cart.pop(product_id_str, None)
        elif action == 'remove':
            cart.pop(product_id_str, None)
        
        # Validate entire cart after changes
        if request.user.is_authenticated:
            cart, changes_made, change_messages = validate_and_clean_cart(request.user, cart)
        
        request.session['cart'] = cart
        
        # Sync cart to database for authenticated users
        if request.user.is_authenticated:
            save_cart_to_database(request.user, cart)
        
        # Recalculate cart totals
        product_ids = list(cart.keys())
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        cart_items = []
        total = 0
        for product in products:
            qty = cart.get(str(product.id), 0)
            price = product.discount_price or product.price
            subtotal = price * qty
            total += subtotal
            cart_items.append({
                'product_id': product.id,
                'quantity': qty,
                'price': float(price),
                'subtotal': float(subtotal),
            })
        
        return JsonResponse({
            'success': True,
            'cart_items': cart_items,
            'total': float(total),
            'cart_count': sum(cart.values()),
            'message': 'Cart updated successfully'
        })
        
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@csrf_exempt
def update_cart_batch(request):
    """Batched cart operations endpoint - processes multiple operations in one request"""
    try:
        data = json.loads(request.body)
        operations = data.get('ops', [])
        client_rev = data.get('client_rev', 0)
        
        if not operations:
            return JsonResponse({'success': False, 'error': 'No operations provided'}, status=400)
        
        cart = request.session.get('cart', {})
        notices = []
        
        # Process all operations in one transaction
        with transaction.atomic():
            # Get all affected products in one query
            product_ids = [str(op.get('product_id')) for op in operations if op.get('product_id')]
            products = {str(p.id): p for p in Product.objects.filter(id__in=product_ids, is_active=True)}
            
            for op in operations:
                product_id = str(op.get('product_id'))
                action = op.get('action', 'update')
                
                # Skip if product doesn't exist
                if product_id not in products:
                    notices.append({
                        'product_id': product_id,
                        'type': 'error',
                        'message': _('Product not found')
                    })
                    continue
                
                product = products[product_id]
                
                if action == 'update':
                    quantity = int(op.get('quantity', 1))
                    
                    if quantity > 0:
                        # Validate quantity against stock
                        original_qty = quantity
                        if quantity > product.stock:
                            quantity = product.stock
                            notices.append({
                                'product_id': product_id,
                                'type': 'stock_adjustment',
                                'message': _('Quantity adjusted to available stock: %(stock)s') % {'stock': product.stock},
                                'adjusted_quantity': quantity
                            })
                        
                        cart[product_id] = quantity
                    else:
                        # Remove if quantity is 0 or negative
                        cart.pop(product_id, None)
                        notices.append({
                            'product_id': product_id,
                            'type': 'removed',
                            'message': _('Item removed from cart')
                        })
                
                elif action == 'remove':
                    cart.pop(product_id, None)
                    notices.append({
                        'product_id': product_id,
                        'type': 'removed',
                        'message': _('Item removed from cart')
                    })
        
        # Validate entire cart after all changes
        if request.user.is_authenticated:
            cart, changes_made, change_messages = validate_and_clean_cart(request.user, cart)
            if change_messages:
                for msg in change_messages:
                    notices.append({
                        'type': 'validation',
                        'message': str(msg)
                    })
        
        request.session['cart'] = cart
        
        # Sync cart to database for authenticated users
        if request.user.is_authenticated:
            save_cart_to_database(request.user, cart)
        
        # Prepare response with canonical cart state
        product_ids = list(cart.keys())
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        cart_items = []
        total = 0
        
        for product in products:
            qty = cart.get(str(product.id), 0)
            price = product.discount_price or product.price
            subtotal = price * qty
            total += subtotal
            cart_items.append({
                'product_id': product.id,
                'quantity': qty,
                'price': float(price),
                'subtotal': float(subtotal),
                'name': product.name,
                'stock': product.stock
            })
        
        return JsonResponse({
            'success': True,
            'cart': {
                'items': cart_items,
                'total': float(total),
                'count': sum(cart.values())
            },
            'server_rev': client_rev + 1,
            'notices': notices,
            'total': float(total),
            'cart_count': sum(cart.values()),
            'message': _('Cart updated successfully')
        })
        
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'success': False, 'error': _('Invalid data format')}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
