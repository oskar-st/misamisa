from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.urls import path
from shop.models import Order, OrderItem, Category, Product, ShippingMethod, PaymentMethod, UserCart
from accounts.models import CustomUser, Address
from accounts.admin import CustomUserAdmin, AddressAdmin
from shop.admin import CategoryAdmin, ProductAdmin, OrderAdmin, OrderItemAdmin, ShippingMethodAdmin, PaymentMethodAdmin

class CustomAdminSite(admin.AdminSite):
    site_header = ''  # Remove all admin header text
    site_title = ''  # Remove all admin title text
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('modules/', self.admin_view(self.module_management_view), name='module_management'),
            path('downloads/', self.admin_view(self.downloads_management_view), name='downloads_management'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """Override the admin index to add dashboard link"""
        extra_context = extra_context or {}
        extra_context['show_dashboard_link'] = True
        extra_context['show_module_management'] = True
        extra_context['show_downloads_management'] = True
        return super().index(request, extra_context)
    
    def dashboard_view(self, request):
        """Custom admin dashboard with business metrics"""
        today = timezone.now().date()
        
        # New orders today
        new_orders_today = Order.objects.filter(
            created_at__date=today
        ).count()
        
        # Revenue (sum of order items)
        total_revenue = OrderItem.objects.aggregate(
            total=Sum('price')
        )['total'] or 0
        
        # Newsletter subscribers
        newsletter_subscribers = CustomUser.objects.filter(
            newsletter_opt_in=True
        ).count()
        
        # Active customers (users with orders)
        active_customers = CustomUser.objects.filter(
            orders__isnull=False
        ).distinct().count()
        
        # Recent orders
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
        
        # Top products by sales
        top_products = OrderItem.objects.values(
            'product__name'
        ).annotate(
            total_sales=Sum('quantity')
        ).order_by('-total_sales')[:5]
        
        # Monthly revenue for the last 6 months
        monthly_revenue = []
        for i in range(6):
            month_start = today.replace(day=1) - timedelta(days=30*i)
            month_end = month_start.replace(day=1) + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            
            month_revenue = OrderItem.objects.filter(
                order__created_at__date__range=[month_start, month_end]
            ).aggregate(
                total=Sum('price')
            )['total'] or 0
            
            monthly_revenue.append({
                'month': month_start.strftime('%B %Y'),
                'revenue': month_revenue
            })
        
        context = {
            'title': _('Admin Dashboard'),
            'new_orders_today': new_orders_today,
            'total_revenue': total_revenue,
            'newsletter_subscribers': newsletter_subscribers,
            'active_customers': active_customers,
            'recent_orders': recent_orders,
            'top_products': top_products,
            'monthly_revenue': monthly_revenue,
            'opts': Order._meta,  # For admin template compatibility
        }
        
        return render(request, 'admin/dashboard.html', context)
    
    def module_management_view(self, request):
        """Redirect to module management interface"""
        return redirect('modules:module_list')
    
    def downloads_management_view(self, request):
        """Redirect to downloads management interface"""
        return redirect('downloads')

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__status']
    search_fields = ['product__name', 'order__customer_email']
    readonly_fields = ['total_price']
    
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = _('Total Price')

class UserCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'total_price', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = _('Total Price')

# Create custom admin site instance
admin_site = CustomAdminSite(name='custom_admin')

# Register all models with the custom admin site
admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Address, AddressAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(OrderItem, OrderItemAdmin)
admin_site.register(UserCart, UserCartAdmin)
admin_site.register(ShippingMethod, ShippingMethodAdmin)
admin_site.register(PaymentMethod, PaymentMethodAdmin) 