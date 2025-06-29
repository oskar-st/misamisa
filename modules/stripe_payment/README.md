# Stripe Payment Module

A Django module for integrating Stripe payment processing into your e-commerce application.

## Features

- Credit card payment processing via Stripe
- Secure payment form with Stripe Elements
- Webhook support for payment notifications
- Admin configuration interface
- Transaction tracking and logging
- Internationalization support

## Installation

1. Upload the module ZIP file to your Django application
2. Install the required dependencies:
   ```bash
   pip install stripe>=5.0.0
   ```
3. Configure your Stripe API keys in the admin panel
4. Set up webhooks in your Stripe Dashboard

## Configuration

### API Keys

You need to configure the following settings:

- **STRIPE_PUBLIC_KEY**: Your Stripe publishable key (starts with `pk_test_` or `pk_live_`)
- **STRIPE_SECRET_KEY**: Your Stripe secret key (starts with `sk_test_` or `sk_live_`)
- **STRIPE_WEBHOOK_SECRET**: Your Stripe webhook endpoint secret (optional)

### Webhook Setup

1. Go to your Stripe Dashboard
2. Navigate to Developers > Webhooks
3. Add endpoint: `https://yourdomain.com/stripe_payment/webhook/`
4. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`
5. Copy the webhook secret and paste it in the admin configuration

## Usage

The module automatically integrates with your checkout process. When a customer selects Stripe as their payment method, they will see a secure payment form with:

- Credit card input (via Stripe Elements)
- Email address field
- Name on card field

## Security

- All sensitive data is handled by Stripe
- No credit card data is stored on your server
- Uses Stripe's secure tokenization system
- Webhook signature verification

## Support

For issues with this module, please check:
1. Your Stripe API keys are correctly configured
2. Webhooks are properly set up
3. The `stripe` Python package is installed

For Stripe-specific issues, refer to the [Stripe Documentation](https://stripe.com/docs). 