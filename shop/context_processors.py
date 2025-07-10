from shop.models import Category

def top_categories(request):
    return {
        'top_categories': Category.objects.filter(parent=None, is_active=True).prefetch_related(
            'children__children__children__children__children'  # Prefetch 5 levels deep for unlimited nesting
        ).order_by('name')
    } 