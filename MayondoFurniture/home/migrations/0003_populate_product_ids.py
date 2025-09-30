# Generated manually for auto-generated product IDs

from django.db import migrations
from datetime import datetime


def populate_product_ids(apps, schema_editor):
    """
    Populate product_id fields for existing Sale and Stock records
    """
    Sale = apps.get_model('home', 'Sale')
    Stock = apps.get_model('home', 'Stock')
    
    # Populate Sale product IDs
    sale_count = 1
    for sale in Sale.objects.all():
        if not sale.product_id:
            date_str = datetime.now().strftime('%Y%m%d')
            sale.product_id = f'SALE-{date_str}-{sale_count:04d}'
            sale.save()
            sale_count += 1
    
    # Populate Stock product IDs
    stock_count = 1
    for stock in Stock.objects.all():
        if not stock.product_id:
            date_str = datetime.now().strftime('%Y%m%d')
            category = stock.product_name[:3].upper() if stock.product_name else 'GEN'
            stock.product_id = f'STK-{category}-{date_str}-{stock_count:04d}'
            stock.save()
            stock_count += 1


def reverse_populate_product_ids(apps, schema_editor):
    """
    Reverse operation - clear product_id fields
    """
    Sale = apps.get_model('home', 'Sale')
    Stock = apps.get_model('home', 'Stock')
    
    Sale.objects.update(product_id='')
    Stock.objects.update(product_id='')


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_notification'),
    ]

    operations = [
        migrations.RunPython(populate_product_ids, reverse_populate_product_ids),
    ]