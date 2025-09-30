from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime

# ===== MAYONDO FURNITURE MANAGEMENT SYSTEM MODELS =====
# This file defines the database structure for the furniture business

class Sale(models.Model):
    """
    Sale Model - Represents individual sales transactions
    Stores information about each sale including product details, customer info, and payment method
    """
    
    # Dropdown choices for product categories (must match Stock categories)
    CUSTOMER_CHOICES = [('Timber', 'Timber'), ('Sofa', 'Sofa'),('Tables','Tables'),('Cupboards','Cupboards'),('Drawer','Drawer'),('Poles','Poles')]
    
    # Product type choices
    PRODUCT_TYPE_CHOICES = [('Wood', 'Wood'), ('Furniture', 'Furniture')]
    
    # Payment method options available to customers
    PAYMENT_CHOICES = [('Cash', 'Cash'), ('Cheque','Cheque'), ('Bank Overdraft','Bank Overdraft')]

    # Product identification - auto-generated unique ID
    product_id = models.CharField(max_length=50, blank=True, unique=True)
    
    # Customer information
    customer_name = models.CharField(max_length=100)
    
    # Product details with category restrictions
    product_name = models.TextField(choices = CUSTOMER_CHOICES)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    
    # Sale quantity and timing
    quantity = models.IntegerField()  # Number of items sold
    date = models.DateField(null=False)  # When the sale occurred
    
    # Payment and logistics
    payment_type = models.TextField(choices = PAYMENT_CHOICES)  # How customer paid
    sales_agent = models.CharField(max_length=50)  # Employee who made the sale
    transport_required = models.BooleanField(default=False)  # Delivery needed (checkbox)

    def save(self, *args, **kwargs):
        """
        Auto-generate product_id for sales if not provided
        Format: SALE-YYYYMMDD-XXXX (e.g., SALE-20251229-0001)
        """
        if not self.product_id:
            # Get current date for ID formatting
            date_str = datetime.now().strftime('%Y%m%d')
            
            # Find the latest sale ID for today
            today_sales = Sale.objects.filter(
                product_id__startswith=f'SALE-{date_str}'
            ).order_by('product_id').last()
            
            if today_sales:
                # Extract the sequence number and increment
                last_seq = int(today_sales.product_id.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            # Generate new product ID
            self.product_id = f'SALE-{date_str}-{new_seq:04d}'
        
        super().save(*args, **kwargs)



class Stock(models.Model):
    """
    Stock Model - Represents inventory items in the furniture store
    Tracks all products available for sale including pricing and supplier information
    """
    
    # Product categories available in the furniture business
    CUSTOMER_CHOICES = [('Timber', 'Timber'), ('Sofa', 'Sofa'),('Tables','Tables'),('Cupboards','Cupboards'),('Drawer','Drawer'),('Poles','Poles')]
    
    # Product type choices
    PRODUCT_TYPE_CHOICES = [('Wood', 'Wood'), ('Furniture', 'Furniture')]
    
    # Origin/Region choices
    ORIGIN_CHOICES = [('Western', 'Western'), ('Central', 'Central'), ('Eastern', 'Eastern')]

    # Product identification and basic info
    product_id = models.CharField(max_length=50, blank=True, unique=True)  # Auto-generated unique identifier
    date = models.DateField()  # Date when item was added to inventory
    product_name = models.TextField(choices=CUSTOMER_CHOICES)  # Product category
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)  # Specific type within category
    
    # Inventory management
    quantity = models.IntegerField()  # Number of items available
    supplier_name = models.CharField(max_length=100)  # Who supplied this product
    
    # Pricing information (stored as CharField for flexibility)
    cost = models.CharField()  # Total cost price
    price = models.CharField()  # Unit selling price
    
    # Additional details
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES)  # Where the product came from

    def save(self, *args, **kwargs):
        """
        Auto-generate product_id for stock items if not provided
        Format: STK-CATEGORY-YYYYMMDD-XXXX (e.g., STK-SOFA-20251229-0001)
        """
        if not self.product_id:
            # Get current date and category for ID formatting
            date_str = datetime.now().strftime('%Y%m%d')
            category = self.product_name.upper()[:3] if self.product_name else 'GEN'
            
            # Find the latest stock ID for this category today
            today_stocks = Stock.objects.filter(
                product_id__startswith=f'STK-{category}-{date_str}'
            ).order_by('product_id').last()
            
            if today_stocks:
                # Extract the sequence number and increment
                last_seq = int(today_stocks.product_id.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            # Generate new product ID
            self.product_id = f'STK-{category}-{date_str}-{new_seq:04d}'
        
        super().save(*args, **kwargs)


class Notification(models.Model):
    """
    Notification Model - Handles system notifications for users
    Used to notify managers and employees about important activities and updates
    """
    
    # Links notification to a specific user (Manager or Employee)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    
    # Notification content and metadata
    message = models.CharField(max_length=255)  # The notification text
    activity_type = models.CharField(max_length=50, default="info")  # Type: info, warning, success, etc.
    
    # Status tracking
    is_read = models.BooleanField(default=False)  # Whether user has seen the notification
    created_at = models.DateTimeField(auto_now_add=True)  # When notification was created

    def __str__(self):
        """String representation for admin interface"""
        return self.message



