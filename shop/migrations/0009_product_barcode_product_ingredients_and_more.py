# Generated by Django 5.2.1 on 2025-07-20 21:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_usercart'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='barcode',
            field=models.CharField(blank=True, max_length=100, verbose_name='barcode'),
        ),
        migrations.AddField(
            model_name='product',
            name='ingredients',
            field=models.TextField(blank=True, verbose_name='ingredients'),
        ),
        migrations.AddField(
            model_name='product',
            name='nutritional_info',
            field=models.JSONField(blank=True, default=dict, verbose_name='nutritional information'),
        ),
        migrations.AddField(
            model_name='product',
            name='package_dimensions',
            field=models.CharField(blank=True, max_length=100, verbose_name='package dimensions'),
        ),
        migrations.AddField(
            model_name='product',
            name='shelf_life_days',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='shelf life (days)'),
        ),
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.CharField(blank=True, max_length=100, verbose_name='SKU'),
        ),
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='weight (g)'),
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/', verbose_name='image')),
                ('alt_text', models.CharField(blank=True, max_length=200, verbose_name='alt text')),
                ('is_primary', models.BooleanField(default=False, verbose_name='is primary image')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='order')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='shop.product', verbose_name='product')),
            ],
            options={
                'verbose_name': 'product image',
                'verbose_name_plural': 'product images',
                'ordering': ['order', 'created_at'],
            },
        ),
    ]
