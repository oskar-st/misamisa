from shop.models import Product

def cart_info(request):
    cart = request.session.get('cart', {})
    count = 0
    total = 0
    if cart:
        products = Product.objects.filter(id__in=cart.keys(), is_active=True)
        for product in products:
            qty = cart.get(str(product.id), 0)
            price = product.discount_price or product.price
            count += qty
            total += price * qty
    return {
        'cart_count': count,
        'cart_total': total,
    } 