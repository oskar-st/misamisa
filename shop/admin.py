from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Category, Product, Order, OrderItem, ShippingMethod, PaymentMethod

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'level', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'parent', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def level(self, obj):
        """Display the nesting level with indentation"""
        return format_html(
            '<span style="margin-left: {}px;">{}</span>',
            obj.level * 20,
            obj.level
        )
    level.short_description = _('Level')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price', 'current_price', 'stock', 'is_active', 'image_preview')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'slug', 'description', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    list_select_related = ('category',)
    ordering = ('category__name', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'is_active')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Inventory', {
            'fields': ('stock',)
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    
    def current_price(self, obj):
        """Display the current price with discount indicator"""
        if obj.has_discount:
            return format_html(
                '<span style="color: red; text-decoration: line-through;">{}</span> <span style="color: green; font-weight: bold;">{}</span>',
                obj.price,
                obj.current_price
            )
        return obj.price
    current_price.short_description = _('Current Price')
    
    def image_preview(self, obj):
        """Display a thumbnail preview of the product image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return _('No image')
    image_preview.short_description = _('Image')

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'estimated_days', 'is_active', 'created_at')
    list_filter = ('is_active', 'estimated_days', 'created_at')
    search_fields = ('name',)
    ordering = ('price',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'price', 'estimated_days', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'is_active', 'created_at')
    list_filter = ('is_active', 'type', 'created_at')
    search_fields = ('name', 'type')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('total_price',)
    fields = ('product', 'quantity', 'price', 'total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'item_count', 'created_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'id')
    readonly_fields = ('created_at', 'updated_at', 'total_amount', 'item_count')
    inlines = [OrderItemInline]
    list_select_related = ('user', 'shipping_address', 'billing_address')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address'),
            'description': 'Select shipping and billing addresses for this order'
        }),
        ('Order Summary', {
            'fields': ('total_amount', 'item_count'),
            'classes': ('collapse',),
            'description': 'Calculated totals based on order items'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_amount(self, obj):
        """Display the total amount with currency formatting"""
        return format_html('<strong>${}</strong>', obj.total_amount)
    total_amount.short_description = _('Total Amount')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_price')
    list_filter = ('order__status', 'order__created_at')
    search_fields = ('order__id', 'product__name', 'order__user__email')
    readonly_fields = ('total_price',)
    list_select_related = ('order', 'product')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'product')
        }),
        ('Item Details', {
            'fields': ('quantity', 'price', 'total_price')
        }),
    )
