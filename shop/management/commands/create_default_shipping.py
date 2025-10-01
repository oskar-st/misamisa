from django.core.management.base import BaseCommand
from shop.models import ShippingMethod


class Command(BaseCommand):
    help = 'Create default shipping methods for testing'

    def handle(self, *args, **options):
        # Create default shipping methods if they don't exist
        shipping_methods = [
            {
                'name': 'Kurier InPost Kurier',
                'price': 17.99,
                'estimated_days': 1,
            },
            {
                'name': 'Paczkomat InPost',
                'price': 12.99,
                'estimated_days': 1,
            },
            {
                'name': 'Sklep Neonet - Nowość',
                'price': 0.00,
                'estimated_days': 2,
            },
        ]

        created_count = 0
        for method_data in shipping_methods:
            method, created = ShippingMethod.objects.get_or_create(
                name=method_data['name'],
                defaults={
                    'price': method_data['price'],
                    'estimated_days': method_data['estimated_days'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created shipping method: {method.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Shipping method already exists: {method.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Setup complete! Created {created_count} new shipping methods.')
        )
