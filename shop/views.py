from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from .models import Category, Product
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse
from shop.models import ShippingMethod, PaymentMethod, Order, OrderItem
from accounts.models import Address, CustomUser
from django.utils import timezone

def product_list(request):
    """Display all active products (admin view)"""
    products = Product.objects.filter(is_active=True).select_related('category')
    context = {
        'products': products,
        'title': _('All Products')
    }
    return render(request, 'shop/product_list.html', context)

def category_detail(request, slug):
    """Display products in a specific category (admin view)"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category')
    
    context = {
        'category': category,
        'products': products,
        'title': category.name
    }
    return render(request, 'shop/category_detail.html', context)

def product_detail(request, slug):
    """Display a specific product (admin view)"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    context = {
        'product': product,
        'title': product.name
    }
    return render(request, 'shop/product_detail.html', context)

# --- PUBLIC VIEWS ---
def product_list_public(request):
    category_slug = request.GET.get('kategoria')
    category = None
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=category)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'shop/public_product_list.html', {
        'categories': categories,
        'category': category,
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'title': _('Shop'),
    })

def product_detail_public(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    # For now, just show product info and a simple add-to-cart form (no JS)
    return render(request, 'shop/public_product_detail.html', {
        'product': product,
        'title': product.name,
    })

def cart_view(request):
    # Cart is stored in session as {product_id: quantity}
    cart = request.session.get('cart', {})
    message = None
    # Handle add, update, remove
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action', 'add')
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except (Product.DoesNotExist, ValueError, TypeError):
            product = None
        if product:
            if action == 'add':
                qty = int(request.POST.get('quantity', 1))
                if product_id in cart:
                    cart[product_id] += qty
                else:
                    cart[product_id] = qty
                message = _('Added to cart.')
            elif action == 'update':
                qty = int(request.POST.get('quantity', 1))
                if qty > 0:
                    cart[product_id] = qty
                    message = _('Cart updated.')
                else:
                    cart.pop(product_id, None)
                    message = _('Item removed.')
            elif action == 'remove':
                cart.pop(product_id, None)
                message = _('Item removed.')
        request.session['cart'] = cart
        return HttpResponseRedirect(reverse('cart_view'))
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
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'message': message,
        'title': _('Cart'),
    })

def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        return HttpResponseRedirect(reverse('cart_view'))
    # Prepare cart items
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
    shipping_methods = ShippingMethod.objects.filter(is_active=True).order_by('price')
    payment_methods = PaymentMethod.objects.filter(is_active=True).order_by('name')
    error = None
    if request.method == 'POST':
        # Collect form data
        name = request.POST.get('name', '').strip()
        street = request.POST.get('street', '').strip()
        city = request.POST.get('city', '').strip()
        postcode = request.POST.get('postcode', '').strip()
        country = request.POST.get('country', '').strip()
        phone = request.POST.get('phone', '').strip()
        shipping_method_id = request.POST.get('shipping_method')
        payment_method_id = request.POST.get('payment_method')
        # Basic validation
        if not all([name, street, city, postcode, country, phone, shipping_method_id, payment_method_id]):
            error = _('Please fill in all required fields.')
        else:
            shipping_method = ShippingMethod.objects.filter(id=shipping_method_id, is_active=True).first()
            payment_method = PaymentMethod.objects.filter(id=payment_method_id, is_active=True).first()
            if not shipping_method or not payment_method:
                error = _('Invalid shipping or payment method.')
        if not error:
            # Create guest user (or use anonymous)
            user = None
            if request.user.is_authenticated:
                user = request.user
            else:
                user = CustomUser.objects.filter(email='guest@misamisa.pl').first()
                if not user:
                    user = CustomUser.objects.create(email='guest@misamisa.pl', first_name='Guest', is_active=False)
            # Create address (for both shipping and billing for now)
            address = Address.objects.create(
                user=user,
                address_type='shipping',
                is_default=False,
                name=name,
                street=street,
                city=city,
                postcode=postcode,
                country=country,
                phone=phone,
            )
            # Create order
            order = Order.objects.create(
                user=user,
                shipping_address=address,
                billing_address=address,
                status='pending',
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price'],
                )
            # Optionally: store shipping/payment method in order (extend model if needed)
            # Clear cart
            request.session['cart'] = {}
            return HttpResponseRedirect(reverse('order_success'))
    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'shipping_methods': shipping_methods,
        'payment_methods': payment_methods,
        'error': error,
        'title': _('Checkout'),
    })
