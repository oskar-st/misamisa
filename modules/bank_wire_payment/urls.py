from django.urls import path
from . import views

app_name = 'bank_wire_payment'

urlpatterns = [
    path('payment_form/', views.payment_form, name='payment_form'),
    path('payment_process/', views.payment_process, name='payment_process'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_error/', views.payment_error, name='payment_error'),
] 