from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Category, Product, Order, OrderItem, ShippingMethod, PaymentMethod
from django import forms

# Conditional import for MPTT admin with drag & drop
try:
    from django_mptt_admin.admin import DjangoMpttAdmin
    MPTT_ADMIN_AVAILABLE = True
except ImportError:
    MPTT_ADMIN_AVAILABLE = False
    # Fallback to regular Django admin
    DjangoMpttAdmin = admin.ModelAdmin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.http import HttpResponseRedirect
from django.utils.http import urlencode

@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    list_display = ("name", "parent", "is_active", "created_at")
    list_display_links = ("name",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "parent", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

class AssignCategoryForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True, label=_('Category'))

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
    
    actions = ["redirect_assign_category"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('assign-category/', self.admin_site.admin_view(self.assign_category_view), name='shop_product_assign_category'),
        ]
        return custom_urls + urls

    def redirect_assign_category(self, request, queryset):
        selected = queryset.values_list('pk', flat=True)
        url = reverse('admin:shop_product_assign_category')
        params = urlencode({'ids': ','.join(str(pk) for pk in selected)})
        return HttpResponseRedirect(f'{url}?{params}')
    redirect_assign_category.short_description = _('Assign category to selected products (custom view)')

    def assign_category_view(self, request):
        ids = request.GET.get('ids') or request.POST.get('ids')
        if not ids:
            self.message_user(request, _('No products selected.'), messages.ERROR)
            return HttpResponseRedirect(reverse('admin:shop_product_changelist'))
        id_list = [int(pk) for pk in ids.split(',') if pk.isdigit()]
        products = Product.objects.filter(pk__in=id_list)
        if request.method == 'POST':
            form = AssignCategoryForm(request.POST)
            if form.is_valid():
                category = form.cleaned_data['category']
                updated = products.update(category=category)
                self.message_user(request, _(f"{updated} products assigned to category '{category}'."), messages.SUCCESS)
                return HttpResponseRedirect(reverse('admin:shop_product_changelist'))
        else:
            form = AssignCategoryForm()
        return render(request, 'admin/shop/assign_category_action.html', {
            'products': products,
            'form': form,
            'ids': ','.join(str(pk) for pk in id_list),
            'title': _('Assign Category to Products'),
        })

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
