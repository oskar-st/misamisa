from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Category, Product, ProductImage, Order, OrderItem, ShippingMethod, PaymentMethod
from django import forms
import json

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
    
    # MPTT Admin configuration for better drag & drop
    tree_auto_open = 0  # Don't auto-expand
    tree_load_on_demand = False  # Load all nodes for drag/drop
    mptt_level_indent = 20  # Indentation per level
    
    # Enhanced admin with auto-refresh
    class Media:
        js = ('admin/js/enhanced_tree_admin.js',)
        css = {
            'all': ('admin/css/enhanced_tree_admin.css',)
        }
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "parent", "is_active")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'order')

class AssignCategoryForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True, label=_('Category'))

class ProductAdminForm(forms.ModelForm):
    # Nutritional information fields
    energy_value = forms.CharField(
        label=_('Energy value'),
        required=False,
        help_text=_('e.g., 2377 kJ/ 571 kcal')
    )
    fat = forms.CharField(
        label=_('Fat'),
        required=False,
        help_text=_('e.g., 38 g')
    )
    saturated_fatty_acids = forms.CharField(
        label=_('Saturated fatty acids'),
        required=False,
        help_text=_('e.g., 31 g')
    )
    carbohydrates = forms.CharField(
        label=_('Carbohydrates'),
        required=False,
        help_text=_('e.g., 51 g')
    )
    sugars = forms.CharField(
        label=_('Sugars'),
        required=False,
        help_text=_('e.g., 18 g')
    )
    fiber = forms.CharField(
        label=_('Fiber'),
        required=False,
        help_text=_('e.g., 2.7 g')
    )
    protein = forms.CharField(
        label=_('Protein'),
        required=False,
        help_text=_('e.g., 7 g')
    )
    salt = forms.CharField(
        label=_('Salt'),
        required=False,
        help_text=_('e.g., 0.4 g')
    )

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Load existing nutritional info into form fields
            nutritional_info = self.instance.nutritional_info or {}
            self.fields['energy_value'].initial = nutritional_info.get('Energy_value', '')
            self.fields['fat'].initial = nutritional_info.get('Fat', '')
            self.fields['saturated_fatty_acids'].initial = nutritional_info.get('Saturated_fatty_acids', '')
            self.fields['carbohydrates'].initial = nutritional_info.get('Carbohydrates', '')
            self.fields['sugars'].initial = nutritional_info.get('Sugars', '')
            self.fields['fiber'].initial = nutritional_info.get('Fiber', '')
            self.fields['protein'].initial = nutritional_info.get('Protein', '')
            self.fields['salt'].initial = nutritional_info.get('Salt', '')

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Build nutritional_info from form fields
        nutritional_info = {}
        if self.cleaned_data.get('energy_value'):
            nutritional_info['Energy_value'] = self.cleaned_data['energy_value']
        if self.cleaned_data.get('fat'):
            nutritional_info['Fat'] = self.cleaned_data['fat']
        if self.cleaned_data.get('saturated_fatty_acids'):
            nutritional_info['Saturated_fatty_acids'] = self.cleaned_data['saturated_fatty_acids']
        if self.cleaned_data.get('carbohydrates'):
            nutritional_info['Carbohydrates'] = self.cleaned_data['carbohydrates']
        if self.cleaned_data.get('sugars'):
            nutritional_info['Sugars'] = self.cleaned_data['sugars']
        if self.cleaned_data.get('fiber'):
            nutritional_info['Fiber'] = self.cleaned_data['fiber']
        if self.cleaned_data.get('protein'):
            nutritional_info['Protein'] = self.cleaned_data['protein']
        if self.cleaned_data.get('salt'):
            nutritional_info['Salt'] = self.cleaned_data['salt']
        
        # Set nutritional_info (empty dict if no values)
        instance.nutritional_info = nutritional_info if nutritional_info else {}
        
        if commit:
            instance.save()
        return instance

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'category', 'price', 'discount_price', 'current_price', 'stock', 'is_active', 'image_preview')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'slug', 'description', 'category__name', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    list_select_related = ('category',)
    ordering = ('category__name', 'name')
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'is_active')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'discount_price', 'stock', 'sku')
        }),
        ('Product Details', {
            'fields': ('weight', 'shelf_life_days', 'package_dimensions', 'barcode')
        }),
        ('Ingredients', {
            'fields': ('ingredients',),
            'classes': ('collapse',)
        }),
        ('Nutritional Information', {
            'fields': ('energy_value', 'fat', 'saturated_fatty_acids', 'carbohydrates', 'sugars', 'fiber', 'protein', 'salt'),
            'classes': ('collapse',),
            'description': _('Note: Saturated fatty acids are included in total Fat. Sugars are included in total Carbohydrates.')
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
        if obj.primary_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.primary_image.image.url
            )
        return _('No image')
    image_preview.short_description = _('Image')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'alt_text', 'is_primary', 'order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    list_select_related = ('product',)
    ordering = ('product__name', 'order')
    
    fieldsets = (
        ('Image Information', {
            'fields': ('product', 'image', 'alt_text')
        }),
        ('Display Settings', {
            'fields': ('is_primary', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'image_preview')
    
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
