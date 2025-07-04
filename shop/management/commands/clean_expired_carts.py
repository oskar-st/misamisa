"""
Django management command to clean expired cart items.

Usage:
python manage.py clean_expired_carts
python manage.py clean_expired_carts --days 60
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from shop.cart_utils import clean_expired_carts


class Command(BaseCommand):
    help = 'Clean expired cart items from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days after which cart items expire (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        if dry_run:
            # For dry run, count without deleting
            from shop.models import UserCart
            from datetime import timedelta
            cutoff_date = timezone.now() - timedelta(days=days)
            count = UserCart.objects.filter(updated_at__lt=cutoff_date).count()
            
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {count} cart items older than {days} days'
                )
            )
        else:
            # Actually clean the carts
            count = clean_expired_carts(days=days)
            
            if count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully cleaned {count} expired cart items older than {days} days'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('No expired cart items found')
                )
        
        # Show current cart statistics
        from shop.models import UserCart
        total_carts = UserCart.objects.count()
        unique_users = UserCart.objects.values('user').distinct().count()
        
        self.stdout.write(
            f'\nCurrent cart statistics:'
        )
        self.stdout.write(
            f'  - Total cart items: {total_carts}'
        )
        self.stdout.write(
            f'  - Users with cart items: {unique_users}'
        ) 