# Generated migration to fix VAT ID field length

from django.db import migrations, models
import accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_invoicedetails_shippingaddress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoicedetails',
            name='vat_id',
            field=models.CharField(
                blank=True, 
                help_text="Enter VAT ID if you're buying as a company.", 
                max_length=15, 
                validators=[accounts.models.validate_polish_nip], 
                verbose_name='VAT ID (NIP)'
            ),
        ),
    ] 