from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, date
import uuid

# ===== MAYONDO FURNITURE MANAGEMENT SYSTEM MODELS =====
# This file defines the database structure for the furniture business

class Product(models.Model):
    """
    Product Model - Central product catalog for the furniture business
    This eliminates duplicate product names and ensures data consistency
    """
    # Product categories available in the furniture business
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
    description = models.TextField(blank=True, help_text="Optional product description")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'product_type']
        ordering = ['name', 'product_type']
    
    def __str__(self):
        return f"{self.name} ({self.product_type})"


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
    
    # Product details - separate fields for better display and form handling
    product_name = models.CharField(max_length=100, choices=CUSTOMER_CHOICES, 
                                   help_text="Select the product category", 
                                   default='Timber')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, 
                                   help_text="Select the product type", 
                                   default='Furniture')
    
    # Optional: Foreign Key to Product model (for advanced features)
    product_ref = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True, 
                                   help_text="Auto-populated from product details")
    
    # Sale quantity and timing
    quantity = models.IntegerField()  # Number of items sold
    date = models.DateField(null=False)  # When the sale occurred
    
    # Pricing information
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Price per unit in dollars")
    total_sales_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Automatically calculated from quantity × unit price")
    
    # Payment and logistics
    payment_type = models.TextField(choices = PAYMENT_CHOICES)  # How customer paid
    sales_agent = models.CharField(max_length=50)  # Employee who made the sale
    transport_required = models.BooleanField(default=False)  # Delivery needed (checkbox)

    def clean(self):
        """
        Custom validation for Sale model
        - Prevents future date sales
        - Ensures quantity is positive
        - Validates product details are provided
        """
        super().clean()
        
        # Validate date is not in the future
        if self.date and self.date > date.today():
            raise ValidationError({
                'date': 'Sale date cannot be in the future. Please select today\'s date or an earlier date.'
            })
        
        # Validate quantity is positive
        if self.quantity is not None and self.quantity <= 0:
            raise ValidationError({
                'quantity': 'Quantity must be greater than 0. Please enter a positive number.'
            })
        
        # Validate unit price is positive
        if self.unit_price is not None and self.unit_price <= 0:
            raise ValidationError({
                'unit_price': 'Unit price must be greater than 0. Please enter a positive amount.'
            })
        
        # Auto-calculate total sales amount
        if self.quantity is not None and self.unit_price is not None:
            self.total_sales_amount = self.quantity * self.unit_price
        
        # Validate product details if provided (they have defaults, so this is optional validation)
        if self.product_name and self.product_name not in [choice[0] for choice in self.CUSTOMER_CHOICES]:
            raise ValidationError({
                'product_name': 'Invalid product name. Please select from available categories.'
            })
        
        if self.product_type and self.product_type not in [choice[0] for choice in self.PRODUCT_TYPE_CHOICES]:
            raise ValidationError({
                'product_type': 'Invalid product type. Please select Wood or Furniture.'
            })

    def save(self, *args, **kwargs):
        """
        Auto-generate product_id for sales if not provided
        Auto-populate foreign key if legacy fields are used
        Format: SALE-YYYYMMDD-XXXX (e.g., SALE-20251229-0001)
        """
        # Run validation before saving
        self.full_clean()
        
        # Auto-populate foreign key from separate fields
        if self.product_name and self.product_type:
            try:
                self.product_ref = Product.objects.get(name=self.product_name, product_type=self.product_type)
            except Product.DoesNotExist:
                # Create product if it doesn't exist
                self.product_ref = Product.objects.create(
                    name=self.product_name,
                    product_type=self.product_type,
                    description=f"Auto-created from Sale record - {self.product_name} ({self.product_type})"
                )
        
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
    
    # Product details - separate fields for better display and form handling
    product_name = models.CharField(max_length=100, choices=CUSTOMER_CHOICES, 
                                   help_text="Select the product category", 
                                   default='Timber')  # Product category
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, 
                                   help_text="Select the product type", 
                                   default='Furniture')  # Specific type within category
    
    # Optional: Foreign Key to Product model (for advanced features)
    product_ref = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True,
                                   help_text="Auto-populated from product details")
    
    # Inventory management
    quantity = models.IntegerField()  # Number of items available
    supplier_name = models.CharField(max_length=100)  # Who supplied this product
    
    # Pricing information
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, 
                                   help_text="Cost per unit item in dollars")
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, 
                                    help_text="Automatically calculated from quantity × unit cost")
    price = models.CharField(help_text="Unit selling price")  # Unit selling price
    
    # Additional details
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES)  # Where the product came from

    def clean(self):
        """
        Custom validation for Stock model
        - Prevents future date stock entries
        - Ensures quantity is positive
        - Validates pricing is positive (if numeric)
        """
        super().clean()
        
        # Validate date is not in the future
        if self.date and self.date > date.today():
            raise ValidationError({
                'date': 'Stock date cannot be in the future. Please select today\'s date or an earlier date.'
            })
        
        # Validate quantity is not negative (allow 0 for out-of-stock items)
        if self.quantity is not None and self.quantity < 0:
            raise ValidationError({
                'quantity': 'Quantity cannot be negative. Please enter 0 or a positive number.'
            })
        
        # Validate product details if provided (they have defaults, so this is optional validation)
        if self.product_name and self.product_name not in [choice[0] for choice in self.CUSTOMER_CHOICES]:
            raise ValidationError({
                'product_name': 'Invalid product name. Please select from available categories.'
            })
        
        if self.product_type and self.product_type not in [choice[0] for choice in self.PRODUCT_TYPE_CHOICES]:
            raise ValidationError({
                'product_type': 'Invalid product type. Please select Wood or Furniture.'
            })
        
        # Validate unit_cost is positive
        if self.unit_cost is not None and self.unit_cost <= 0:
            raise ValidationError({
                'unit_cost': 'Unit cost must be greater than 0. Please enter a positive amount.'
            })
        
        # Auto-calculate total cost
        if self.quantity is not None and self.unit_cost is not None:
            self.total_cost = self.quantity * self.unit_cost
        
        # Validate price is positive (if it contains numeric values)
        if self.price:
            try:
                price_value = float(self.price.replace(',', ''))  # Remove commas for validation
                if price_value <= 0:
                    raise ValidationError({
                        'price': 'Price must be greater than 0. Please enter a positive amount.'
                    })
            except (ValueError, AttributeError):
                # If price is not numeric, we'll allow it (for flexibility)
                pass

    def save(self, *args, **kwargs):
        """
        Auto-generate product_id for stock items if not provided
        Auto-populate foreign key if legacy fields are used
        Format: STK-YYYYMMDD-XXXX (e.g., STK-20251229-0001)
        """
        # Auto-populate foreign key from separate fields
        if self.product_name and self.product_type:
            try:
                self.product_ref = Product.objects.get(name=self.product_name, product_type=self.product_type)
            except Product.DoesNotExist:
                # Create product if it doesn't exist
                self.product_ref = Product.objects.create(
                    name=self.product_name,
                    product_type=self.product_type,
                    description=f"Auto-created from Stock record - {self.product_name} ({self.product_type})"
                )
        # Run validation before saving
        self.full_clean()
        
        if not self.product_id:
            # Get current date for ID formatting
            date_str = datetime.now().strftime('%Y%m%d')
            
            # Find the latest stock ID for today
            today_stocks = Stock.objects.filter(
                product_id__startswith=f'STK-{date_str}'
            ).order_by('product_id').last()
            
            if today_stocks:
                # Extract the sequence number and increment
                last_seq = int(today_stocks.product_id.split('-')[-1])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            # Generate new product ID
            self.product_id = f'STK-{date_str}-{new_seq:04d}'
        
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

