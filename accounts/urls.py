from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Address management
    path('addresses/', views.addresses_view, name='addresses'),
    
    # Shipping addresses
    path('addresses/shipping/add/', views.add_shipping_address, name='add_shipping_address'),
    path('addresses/shipping/<int:address_id>/edit/', views.edit_shipping_address, name='edit_shipping_address'),
    path('addresses/shipping/<int:address_id>/delete/', views.delete_shipping_address, name='delete_shipping_address'),
    
    # Invoice details
    path('addresses/invoice/add/', views.add_invoice_details, name='add_invoice_details'),
    path('addresses/invoice/<int:details_id>/edit/', views.edit_invoice_details, name='edit_invoice_details'),
    path('addresses/invoice/<int:details_id>/delete/', views.delete_invoice_details, name='delete_invoice_details'),
] 