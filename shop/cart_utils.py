"""
Cart utility functions for handling session and database cart synchronization.
"""

from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import UserCart, Product


def save_cart_to_database(user, session_cart):
    """Save session cart to database for authenticated user."""
    if not user.is_authenticated:
        return
    
    # Clear existing cart items for this user
    UserCart.objects.filter(user=user).delete()
    
    # Save session cart items to database
    for product_id, quantity in session_cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            UserCart.objects.create(
                user=user,
                product=product,
                quantity=quantity
            )
        except Product.DoesNotExist:
            # Skip invalid product IDs
            pass


def load_cart_from_database(user):
    """Load cart from database for authenticated user."""
    if not user.is_authenticated:
        return {}
    
    cart = {}
    user_cart_items = UserCart.objects.filter(user=user).select_related('product')
    
    for item in user_cart_items:
        if item.product.is_active:
            cart[str(item.product.id)] = item.quantity
    
    return cart


def validate_and_clean_cart(user, cart_dict):
    """
    Validate cart against current stock and product availability.
    Returns: (cleaned_cart, changes_made, change_messages)
    """
    if not cart_dict:
        return {}, False, []
    
    cleaned_cart = {}
    changes_made = False
    change_messages = []
    
    for product_id, quantity in cart_dict.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            # Check if product is still available
            if not product.is_active:
                changes_made = True
                change_messages.append(f"'{product.name}' is no longer available and was removed from your cart.")
                continue
            
            # Check stock availability
            available_stock = product.stock
            if quantity > available_stock:
                if available_stock > 0:
                    # Reduce quantity to available stock
                    cleaned_cart[product_id] = available_stock
                    changes_made = True
                    change_messages.append(f"'{product.name}' quantity reduced from {quantity} to {available_stock} (limited stock).")
                else:
                    # Remove item - out of stock
                    changes_made = True
                    change_messages.append(f"'{product.name}' is out of stock and was removed from your cart.")
            else:
                # Keep original quantity
                cleaned_cart[product_id] = quantity
                
        except Product.DoesNotExist:
            # Product no longer exists
            changes_made = True
            change_messages.append("Some items in your cart are no longer available and were removed.")
    
    return cleaned_cart, changes_made, change_messages


def clean_expired_carts(days=30):
    """
    Remove cart items older than specified days.
    Call this from a management command or scheduled task.
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    expired_items = UserCart.objects.filter(updated_at__lt=cutoff_date)
    count = expired_items.count()
    expired_items.delete()
    return count


def merge_carts(session_cart, database_cart):
    """Merge session cart with database cart, prioritizing session cart quantities."""
    merged_cart = database_cart.copy()
    
    for product_id, quantity in session_cart.items():
        merged_cart[product_id] = quantity
    
    return merged_cart


def clear_user_cart(user):
    """Clear user's cart from database."""
    if user.is_authenticated:
        UserCart.objects.filter(user=user).delete()


def sync_cart_on_login(request, user):
    """Synchronize cart when user logs in with validation."""
    if not user.is_authenticated:
        return
    
    # Get session cart
    session_cart = request.session.get('cart', {})
    
    # Get database cart
    database_cart = load_cart_from_database(user)
    
    # Merge carts (session cart takes priority)
    merged_cart = merge_carts(session_cart, database_cart)
    
    # Validate and clean the merged cart
    cleaned_cart, changes_made, change_messages = validate_and_clean_cart(user, merged_cart)
    
    # Update session with cleaned cart
    request.session['cart'] = cleaned_cart
    
    # Save cleaned cart to database
    save_cart_to_database(user, cleaned_cart)
    
    # Store change messages in session for display
    if change_messages:
        request.session['cart_change_messages'] = change_messages


def sync_cart_on_logout(request, user):
    """Synchronize cart when user logs out."""
    if user.is_authenticated:
        # Save current session cart to database
        session_cart = request.session.get('cart', {})
        save_cart_to_database(user, session_cart)
    
    # Keep session cart for anonymous browsing
    # Don't clear the session cart so user can continue shopping
    pass


def get_cart_change_messages(request):
    """Get and clear cart change messages from session."""
    messages = request.session.get('cart_change_messages', [])
    if 'cart_change_messages' in request.session:
        del request.session['cart_change_messages']
    return messages 