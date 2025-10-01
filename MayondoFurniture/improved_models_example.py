# IMPROVED MODELS WITH FOREIGN KEY RELATIONSHIPS
# This shows how to implement proper database relationships

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date

class Product(models.Model):
    """
    Product Model - Central product catalog
    This eliminates duplicate product names and ensures consistency
    """
    # Product categories
    PRODUCT_CHOICES = [
        ('Timber', 'Timber'), 
        ('Sofa', 'Sofa'),
        ('Tables','Tables'),
        ('Cupboards','Cupboards'),
        ('Drawer','Drawer'),
        ('Poles','Poles')
    ]
    
    # Product type choices
    PRODUCT_TYPE_CHOICES = [('Wood', 'Wood'), ('Furniture', 'Furniture')]
    
    name = models.CharField(max_length=50, choices=PRODUCT_CHOICES)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Ensure unique product combinations
    class Meta:
        unique_together = ['name', 'product_type']
    
    def __str__(self):
        return f"{self.name} ({self.product_type})"


class ImprovedSale(models.Model):
    """
    Improved Sale Model with Foreign Key relationship
    """
    # FOREIGN KEY RELATIONSHIP - Much better than string matching!
    product = models.ForeignKey(Product, on_delete=models.PROTECT)  # PROTECT prevents deleting referenced products
    
    # Auto-generated ID
    product_id = models.CharField(max_length=50, blank=True, unique=True)
    
    # Customer and sale details
    customer_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()  # Automatically prevents negative values!
    date = models.DateField()
    
    # Payment choices
    PAYMENT_CHOICES = [('Cash', 'Cash'), ('Cheque','Cheque'), ('Bank Overdraft','Bank Overdraft')]
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    
    sales_agent = models.CharField(max_length=50)
    transport_required = models.BooleanField(default=False)

    def clean(self):
        """Validation - only check date since quantity is PositiveIntegerField"""
        super().clean()
        if self.date and self.date > date.today():
            raise ValidationError({
                'date': 'Sale date cannot be in the future.'
            })

    # Now querying is simple and fast:
    # stock_item = Stock.objects.filter(product=sale.product).first()
    # No more string matching needed!


class ImprovedStock(models.Model):
    """
    Improved Stock Model with Foreign Key relationship
    """
    # FOREIGN KEY RELATIONSHIP
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    # Auto-generated ID
    product_id = models.CharField(max_length=50, blank=True, unique=True)
    
    # Inventory details
    quantity = models.PositiveIntegerField()  # Automatically prevents negative values!
    date = models.DateField()
    supplier_name = models.CharField(max_length=100)
    
    # Pricing - using DecimalField for proper numeric handling
    cost = models.DecimalField(max_digits=10, decimal_places=2)  # Better than CharField!
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Better than CharField!
    
    # Origin choices
    ORIGIN_CHOICES = [('Western', 'Western'), ('Central', 'Central'), ('Eastern', 'Eastern')]
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES)

    def clean(self):
        """Validation for date only - quantity/cost/price handled by field types"""
        super().clean()
        if self.date and self.date > date.today():
            raise ValidationError({
                'date': 'Stock date cannot be in the future.'
            })

    # Benefits of this approach:
    # 1. Fast queries: Stock.objects.filter(product=product_instance)
    # 2. Data integrity: Can't delete products that have stock/sales
    # 3. Consistent naming: Product names are centralized
    # 4. No more MultipleObjectsReturned errors


# MIGRATION STRATEGY (how to convert existing data):
"""
1. Create Product model and migrate
2. Populate Product table with unique combinations from existing Sales/Stock
3. Add foreign key fields to Sale/Stock models
4. Data migration to link existing records to Product instances
5. Remove old product_name/product_type fields
6. Update forms and views to use product foreign key
"""