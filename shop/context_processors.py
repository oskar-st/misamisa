from shop.models import Category

def top_categories(request):
    return {
        'top_categories': Category.objects.filter(parent=None).order_by('name')
    } 