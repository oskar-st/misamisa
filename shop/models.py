from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel):
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True, blank=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('parent category')
    )
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['tree_id', 'lft']

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category_detail', kwargs={'slug': self.slug})

    @property
    def full_path(self):
        """Returns the full category path as a string"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

    @property
    def level(self):
        """Returns the nesting level of the category"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

class Product(models.Model):
    name = models.CharField(_('name'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('category')
    )
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        _('discount price'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    stock = models.PositiveIntegerField(_('stock'), default=0)
    is_active = models.BooleanField(_('is active'), default=True)
    image = models.ImageField(_('image'), upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_or_product', kwargs={'slug': self.slug})

    @property
    def current_price(self):
        """Returns the current price (discount price if available, otherwise regular price)"""
        return self.discount_price if self.discount_price else self.price

    @property
    def has_discount(self):
        """Returns True if the product has a discount"""
        return self.discount_price is not None and self.discount_price < self.price

    @property
    def discount_percentage(self):
        """Returns the discount percentage if applicable"""
        if self.has_discount:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

class ShippingMethod(models.Model):
    name = models.CharField(_('name'), max_length=100)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    estimated_days = models.PositiveIntegerField(_('estimated days'))
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('shipping method')
        verbose_name_plural = _('shipping methods')
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - ${self.price} ({self.estimated_days} days)"

class PaymentMethod(models.Model):
    name = models.CharField(_('name'), max_length=100)
    type = models.CharField(_('type'), max_length=50, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')
        ordering = ['name']

    def __str__(self):
        if self.type:
            return f"{self.name} ({self.type})"
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('shipped', _('Shipped')),
        ('cancelled', _('Cancelled')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('user'),
        null=True,
        blank=True
    )
    shipping_address = models.ForeignKey(
        'accounts.Address',
        on_delete=models.PROTECT,
        related_name='shipping_orders',
        verbose_name=_('shipping address'),
        null=True,
        blank=True
    )
    billing_address = models.ForeignKey(
        'accounts.Address',
        on_delete=models.PROTECT,
        related_name='billing_orders',
        verbose_name=_('billing address'),
        null=True,
        blank=True
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Customer information
    customer_name = models.CharField(
        _('customer name'),
        max_length=200,
        blank=True
    )
    customer_email = models.EmailField(
        _('customer email'),
        blank=True
    )
    
    # Payment information
    payment_method_name = models.CharField(
        _('payment method'),
        max_length=100,
        blank=True
    )
    payment_transaction_id = models.CharField(
        _('transaction ID'),
        max_length=100,
        blank=True
    )
    payment_status = models.CharField(
        _('payment status'),
        max_length=50,
        default='pending'
    )
    total_amount = models.DecimalField(
        _('total amount'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"Order #{self.id} - {self.user.email} ({self.get_status_display()})"
        return f"Order #{self.id} - Guest ({self.get_status_display()})"

    @property
    def calculated_total_amount(self):
        """Calculate the total amount of the order from items"""
        return sum(item.total_price for item in self.items.all())

    @property
    def item_count(self):
        """Get the total number of items in the order"""
        return sum(item.quantity for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('order')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_('product')
    )
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order #{self.order.id}"

    @property
    def total_price(self):
        """Calculate the total price for this item"""
        if self.price is None:
            return 0
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        # Set the price from the product's current price if not already set
        if not self.price:
            self.price = self.product.current_price
        super().save(*args, **kwargs)
