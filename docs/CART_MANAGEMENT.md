# Cart Management System

## Overview

The cart management system provides:
- **Cart Persistence**: User carts are saved to database and restored on login
- **Stock Validation**: Automatic validation against current product stock
- **Cart Expiration**: Automatic cleanup of old cart items
- **Smart Notifications**: User-friendly messages about cart changes

## Features

### 1. Cart Persistence
- Anonymous users: Cart stored in session only
- Authenticated users: Cart synced to database
- Login: Session cart merged with database cart (session takes priority)
- Logout: Cart saved to database, session cleared

### 2. Stock Validation
- **On Login**: Cart validated against current stock
- **On Cart View**: Cart validated when page loads
- **On Cart Operations**: Stock checked when adding/updating items
- **Automatic Adjustments**: Quantities reduced to available stock
- **Item Removal**: Out-of-stock items removed automatically

### 3. Cart Expiration
- **Default**: Cart items expire after 30 days of inactivity
- **Configurable**: Can be adjusted via management command
- **Automatic Cleanup**: Run via cron job or scheduled task

## Usage

### Management Commands

#### Clean Expired Carts
```bash
# Clean carts older than 30 days (default)
python manage.py clean_expired_carts

# Clean carts older than 60 days
python manage.py clean_expired_carts --days 60

# Dry run - see what would be deleted
python manage.py clean_expired_carts --dry-run
```

### Setting Up Automatic Cleanup

#### Option 1: Cron Job (Linux/Unix)
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 2 AM
0 2 * * * cd /var/www/misamisa.pl && source venv/bin/activate && python manage.py clean_expired_carts

# Or weekly on Sunday at 3 AM
0 3 * * 0 cd /var/www/misamisa.pl && source venv/bin/activate && python manage.py clean_expired_carts
```

#### Option 2: Django-crontab (If installed)
```python
# settings.py
CRONJOBS = [
    ('0 2 * * *', 'shop.management.commands.clean_expired_carts.Command', '>> /var/log/django_cron.log'),
]
```

#### Option 3: Celery (If using background tasks)
```python
# tasks.py
from celery import shared_task
from shop.cart_utils import clean_expired_carts

@shared_task
def clean_expired_carts_task():
    count = clean_expired_carts(days=30)
    return f"Cleaned {count} expired cart items"

# Schedule in celery beat
```

## Configuration

### Cart Expiration Settings
You can customize cart expiration by modifying the management command:

```python
# Custom expiration periods
clean_expired_carts(days=7)   # 1 week
clean_expired_carts(days=30)  # 30 days (default)
clean_expired_carts(days=90)  # 3 months
clean_expired_carts(days=365) # 1 year
```

### Stock Validation Behavior
The system automatically:
- Reduces quantities to available stock
- Removes out-of-stock items
- Notifies users of changes
- Preserves user intent when possible

## User Experience

### Messages Displayed to Users

#### Cart Change Messages (Yellow warning alerts)
- "Product X quantity reduced from 5 to 3 (limited stock)"
- "Product Y is out of stock and was removed from your cart"
- "Product Z is no longer available and was removed from your cart"

#### Cart Operation Messages (Green success alerts)
- "Added to cart"
- "Cart updated"
- "Item removed"
- "Quantity adjusted to available stock"
- "Maximum stock reached"

### When Validation Occurs
1. **User Login**: Cart validated and cleaned
2. **Cart Page Load**: Real-time validation for authenticated users
3. **Adding Items**: Stock checked before adding
4. **Updating Quantities**: Stock limits enforced
5. **AJAX Updates**: Stock validation on quantity changes

## Database Schema

### UserCart Model
```python
class UserCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'product']
```

## Best Practices

### Recommended Expiration Periods
- **B2C E-commerce**: 30-60 days
- **B2B Platforms**: 90-180 days
- **High-frequency sites**: 14-30 days
- **Luxury/considered purchases**: 60-90 days

### Monitoring
- Check cleanup logs regularly
- Monitor cart statistics with `--dry-run`
- Alert on unusual cart patterns
- Track user feedback on cart changes

### Performance
- Index on `updated_at` field for efficient cleanup
- Consider batch processing for large datasets
- Run cleanup during low-traffic hours
- Monitor database size and growth

## API Integration

### Cart Utilities Functions
```python
from shop.cart_utils import (
    validate_and_clean_cart,
    clean_expired_carts,
    get_cart_change_messages,
    sync_cart_on_login,
    sync_cart_on_logout
)

# Validate a cart manually
cart, changes, messages = validate_and_clean_cart(user, cart_dict)

# Clean expired carts programmatically
count = clean_expired_carts(days=30)

# Get pending change messages
messages = get_cart_change_messages(request)
```

## Troubleshooting

### Common Issues

#### Cart Not Syncing
- Check user authentication
- Verify database migrations
- Check for JavaScript errors

#### Stock Validation Not Working
- Ensure products have correct stock values
- Check Product.is_active status
- Verify cart validation is called

#### Cleanup Not Running
- Check cron job syntax
- Verify file permissions
- Check Django project path
- Review error logs

### Debugging Commands
```bash
# Check current cart statistics
python manage.py clean_expired_carts --dry-run

# Test cart validation manually
python manage.py shell
>>> from shop.cart_utils import validate_and_clean_cart
>>> # Test validation logic

# Check database content
python manage.py shell
>>> from shop.models import UserCart
>>> UserCart.objects.all().count()
``` 