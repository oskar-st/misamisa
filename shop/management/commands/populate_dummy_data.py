import os
import urllib.request
from django.core.management.base import BaseCommand
from shop.models import Category, Product
from shop.models import ProductImage
from home.models import News
from django.conf import settings
from decimal import Decimal
from urllib.request import Request, urlopen

DUMMY_IMAGE_URLS = [
    'https://images.pexels.com/photos/230325/pexels-photo-230325.jpeg?auto=compress&w=400',  # Cookies
    'https://images.pexels.com/photos/461382/pexels-photo-461382.jpeg?auto=compress&w=400',  # Macarons
    'https://images.pexels.com/photos/704971/pexels-photo-704971.jpeg?auto=compress&w=400',  # Donut
    'https://images.pexels.com/photos/14105/pexels-photo-14105.jpeg?auto=compress&w=400',    # Cupcake
    'https://images.pexels.com/photos/357576/pexels-photo-357576.jpeg?auto=compress&w=400',  # Sweets
]

CATEGORIES = [
    'Cookies',
    'Cakes',
    'Candies',
    'Chocolate',
    'Pastries',
]

PRODUCTS = [
    {'name': 'DUMMY_Chocolate Chip Cookie', 'category': 'Cookies', 'price': '5.99', 'stock': 50, 'desc': 'Classic cookie with chocolate chips.'},
    {'name': 'DUMMY_Macarons', 'category': 'Cookies', 'price': '12.99', 'stock': 30, 'desc': 'Colorful French macarons.'},
    {'name': 'DUMMY_Glazed Donut', 'category': 'Pastries', 'price': '4.50', 'stock': 40, 'desc': 'Sweet donut with sugar glaze.'},
    {'name': 'DUMMY_Cupcake', 'category': 'Cakes', 'price': '6.00', 'stock': 25, 'desc': 'Vanilla cupcake with frosting.'},
    {'name': 'DUMMY_Gummy Bears', 'category': 'Candies', 'price': '3.99', 'stock': 100, 'desc': 'Fruity gummy bear candies.'},
    {'name': 'DUMMY_Milk Chocolate Bar', 'category': 'Chocolate', 'price': '7.50', 'stock': 60, 'desc': 'Smooth milk chocolate bar.'},
    {'name': 'DUMMY_Peanut Butter Cookie', 'category': 'Cookies', 'price': '6.49', 'stock': 40, 'desc': 'Rich peanut butter cookies.'},
    {'name': 'DUMMY_Oatmeal Raisin Cookie', 'category': 'Cookies', 'price': '5.49', 'stock': 35, 'desc': 'Chewy oatmeal cookies with raisins.'},
    {'name': 'DUMMY_Lemon Tart', 'category': 'Cakes', 'price': '8.99', 'stock': 20, 'desc': 'Tangy lemon tart with buttery crust.'},
    {'name': 'DUMMY_Red Velvet Cake', 'category': 'Cakes', 'price': '14.99', 'stock': 15, 'desc': 'Classic red velvet cake with cream cheese frosting.'},
    {'name': 'DUMMY_Sour Gummies', 'category': 'Candies', 'price': '4.29', 'stock': 90, 'desc': 'Sour fruit-flavored gummy candies.'},
    {'name': 'DUMMY_Jelly Beans', 'category': 'Candies', 'price': '3.79', 'stock': 120, 'desc': 'Assorted jelly beans in every flavor.'},
    {'name': 'DUMMY_Dark Chocolate Truffle', 'category': 'Chocolate', 'price': '9.99', 'stock': 30, 'desc': 'Rich dark chocolate truffles.'},
    {'name': 'DUMMY_White Chocolate Bar', 'category': 'Chocolate', 'price': '7.99', 'stock': 50, 'desc': 'Creamy white chocolate bar.'},
    {'name': 'DUMMY_Croissant', 'category': 'Pastries', 'price': '3.50', 'stock': 60, 'desc': 'Flaky, buttery croissant.'},
    {'name': 'DUMMY_Pain au Chocolat', 'category': 'Pastries', 'price': '4.00', 'stock': 55, 'desc': 'French pastry with chocolate filling.'},
    {'name': 'DUMMY_Strawberry Shortcake', 'category': 'Cakes', 'price': '11.99', 'stock': 18, 'desc': 'Shortcake with fresh strawberries and cream.'},
    {'name': 'DUMMY_Brownie', 'category': 'Cakes', 'price': '5.99', 'stock': 40, 'desc': 'Fudgy chocolate brownie.'},
    {'name': 'DUMMY_Caramel Fudge', 'category': 'Candies', 'price': '4.99', 'stock': 80, 'desc': 'Soft caramel fudge squares.'},
    {'name': 'DUMMY_Marshmallow Twists', 'category': 'Candies', 'price': '3.49', 'stock': 110, 'desc': 'Colorful marshmallow twists.'},
    {'name': 'DUMMY_Hazelnut Praline', 'category': 'Chocolate', 'price': '10.49', 'stock': 25, 'desc': 'Chocolate with hazelnut praline filling.'},
    {'name': 'DUMMY_Raspberry Danish', 'category': 'Pastries', 'price': '4.75', 'stock': 35, 'desc': 'Danish pastry with raspberry jam.'},
    {'name': 'DUMMY_Almond Biscotti', 'category': 'Cookies', 'price': '6.99', 'stock': 30, 'desc': 'Crunchy almond biscotti.'},
    {'name': 'DUMMY_Cinnamon Roll', 'category': 'Pastries', 'price': '5.25', 'stock': 45, 'desc': 'Sweet cinnamon roll with icing.'},
]

NEWS = [
    {'title': 'DUMMY_New Cookie Flavors!', 'content': 'Try our new range of cookies, now available in store. We\'ve added exciting flavors like Matcha Green Tea, Salted Caramel, and Dark Chocolate Orange. Limited time offer!'},
    {'title': 'DUMMY_Summer Sweets Sale', 'content': 'Enjoy 20% off on all candies and chocolates this summer! Perfect treats to cool down during hot days. Sale ends August 31st.'},
    {'title': 'DUMMY_Bakery Now Open Sundays', 'content': 'We are now open every Sunday from 9am to 3pm. Start your Sunday morning with our freshly baked croissants and coffee!'},
    {'title': 'DUMMY_Introducing Gluten-Free Options', 'content': 'We\'re excited to announce our new gluten-free product line! Now everyone can enjoy our delicious treats. Try our gluten-free brownies, cookies, and cakes.'},
    {'title': 'DUMMY_Holiday Gift Boxes Pre-Order', 'content': 'Christmas is coming! Pre-order our special holiday gift boxes filled with premium chocolates, cookies, and candies. Perfect for family and corporate gifts.'},
    {'title': 'DUMMY_New Vegan Collection Launch', 'content': 'Introducing our vegan dessert collection! Indulge in our plant-based cakes, cookies, and pastries that taste just as amazing as they look.'},
    {'title': 'DUMMY_Birthday Cake Workshop', 'content': 'Join our cake decorating workshop this weekend! Learn professional techniques for decorating birthday cakes. Limited spots available.'},
    {'title': 'DUMMY_Local Ingredients Partnership', 'content': 'We\'re proud to announce our partnership with local farmers! All our products now use locally sourced ingredients where possible.'}
]

class Command(BaseCommand):
    help = 'Populate the site with dummy categories, products, and news (all marked for easy removal).'

    def handle(self, *args, **options):
        # Create categories
        cat_objs = {}
        for cat in CATEGORIES:
            obj, _ = Category.objects.get_or_create(name=cat, defaults={'slug': f'dummy-{cat.lower()}', 'is_active': True})
            cat_objs[cat] = obj
        self.stdout.write(self.style.SUCCESS('Dummy categories created.'))

        # Download images with custom user-agent
        media_root = settings.MEDIA_ROOT
        img_paths = []
        for idx, url in enumerate(DUMMY_IMAGE_URLS):
            img_path = os.path.join(media_root, f'products/dummy_{idx+1}.jpg')
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
            if not os.path.exists(img_path):
                req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urlopen(req) as response, open(img_path, 'wb') as out_file:
                    out_file.write(response.read())
            img_paths.append(f'products/dummy_{idx+1}.jpg')
        self.stdout.write(self.style.SUCCESS('Dummy images downloaded.'))

        # Create products
        # Use jpgs from downloads/ for images
        downloads_dir = os.path.join(settings.BASE_DIR, 'downloads')
        jpg_files = [f for f in os.listdir(downloads_dir) if f.lower().endswith('.jpg')]
        if not jpg_files:
            self.stdout.write(self.style.WARNING('No jpg files found in downloads/ folder. Products will have no images.'))
        for idx, prod in enumerate(PRODUCTS):
            category = cat_objs[prod['category']]
            product, _ = Product.objects.get_or_create(
                name=prod['name'],
                defaults={
                    'slug': f"dummy-{prod['name'].lower().replace(' ', '-')}" ,
                    'category': category,
                    'description': prod['desc'],
                    'price': Decimal(prod['price']),
                    'stock': prod['stock'],
                    'is_active': True,
                }
            )
            # Attach a ProductImage from downloads/ if available
            if jpg_files:
                img_file = jpg_files[idx % len(jpg_files)]
                img_path = os.path.join(downloads_dir, img_file)
                # Copy to media/products/ for proper serving
                media_img_dir = os.path.join(settings.MEDIA_ROOT, 'products')
                os.makedirs(media_img_dir, exist_ok=True)
                dest_img_path = os.path.join(media_img_dir, img_file)
                if not os.path.exists(dest_img_path):
                    with open(img_path, 'rb') as src, open(dest_img_path, 'wb') as dst:
                        dst.write(src.read())
                rel_img_path = f'products/{img_file}'
                # Only add if not already present
                if not product.images.filter(image=rel_img_path).exists():
                    ProductImage.objects.create(
                        product=product,
                        image=rel_img_path,
                        alt_text=product.name,
                        is_primary=True,
                        order=0
                    )
        self.stdout.write(self.style.SUCCESS('Dummy products created.'))

        # Create news
        for news in NEWS:
            News.objects.get_or_create(
                title=news['title'],
                defaults={
                    'content': news['content'],
                    'is_dummy': True,
                }
            )
        self.stdout.write(self.style.SUCCESS('Dummy news created.'))

        self.stdout.write(self.style.SUCCESS('All dummy data populated!')) 