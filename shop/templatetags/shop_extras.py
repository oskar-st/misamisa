from django import template
from django.templatetags.static import static
from django.conf import settings
import random
import os

register = template.Library()

@register.filter
def get_product_image(product):
    """
    Returns the product's primary image or a placeholder cookie image if none exists or file is missing.
    """
    if product.primary_image and product.primary_image.image:
        # Check if the image file actually exists
        image_path = os.path.join(settings.MEDIA_ROOT, str(product.primary_image.image))
        if os.path.exists(image_path):
            return product.primary_image.image.url
    
    # Return a random cookie placeholder image if no image or file doesn't exist
    cookie_images = [
        'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1606312619070-d48b4c652a52?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1606312619070-d48b4c652a52?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1606312619070-d48b4c652a52?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&h=400&fit=crop',
    ]
    return random.choice(cookie_images)

@register.filter
def get_product_alt_text(product):
    """
    Returns the product's image alt text or a default cookie description.
    """
    if product.primary_image and product.primary_image.alt_text:
        return product.primary_image.alt_text
    else:
        cookie_descriptions = [
            'Delicious chocolate chip cookie',
            'Fresh baked cookie',
            'Homemade cookie',
            'Sweet cookie treat',
            'Yummy cookie',
            'Fresh cookie',
            'Delicious cookie',
            'Baked cookie',
            'Sweet treat cookie',
            'Homemade treat cookie',
        ]
        return random.choice(cookie_descriptions) 