"""
MAYONDO F# Dja# Django imports
from django import forms   # Django's form system
from datetime import date as today_date   # For date validation

# Local importsimports
from django import forms   # Django's form system
from datetime import date   # For date validation

# Local imports
from .models import Sale, Stock   # Import the database models (Sale and Stock)URE MANAGEMENT SYSTEM - FORMS
=============================================

This file defines all the forms used in the application using Django's ModelForm
and django-crispy-forms for professional styling and layout.

Forms included:
- SaleForm: For creating new sales records
- StockForm: For adding new inventory items  
- SaleViewForm: Read-only view of existing sales
- StockViewForm: Read-only view of existing stock
"""

# Django imports
from django import forms   # Django’s form system

# Local imports
from .models import Sale, Stock, Product, Customer, Supplier   # Import the database models

# Crispy forms imports - minimal setup for template-based forms
from crispy_forms.helper import FormHelper   # Basic form helper


class SaleForm(forms.ModelForm):
    """
    Sale Form - Creates and edits sales records
    Features professional styling with Tailwind CSS integration
    Includes validation and user-friendly field layouts
    """
    
    # Override customer field to use dropdown of registered customers
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all().order_by('name'),
        empty_label="-- Select Customer --",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cordes-blue focus:border-transparent',
            'title': 'Select a registered customer from the dropdown'
        }),
        help_text='Select from registered customers. If no customers are available, please add a new customer first.',
        error_messages={
            'required': 'Please select a customer from the dropdown.',
            'invalid_choice': 'Please select a valid customer from the list.'
        }
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Update help text based on available customers
        if not Customer.objects.exists():
            self.fields['customer'].empty_label = "-- No customers available. Add a customer first --"
            self.fields['customer'].help_text = 'No customers are registered yet. Please add a customer before creating a sale.'
    
    class Meta:
        model = Sale   # This form is based on the Sale model
        fields = ['customer', 'product_name', 'product_type', 'quantity', 'unit_price', 'total_sales_amount', 
                 'date', 'payment_type', 'sales_agent', 'transport_required']
        # Using separate product_name and product_type fields for better display
        
        # Custom error messages for better user experience
        error_messages = {
            # customer_name errors are now handled in the field definition above
            'product_name': {
                'required': 'Product name is required. Please select a product category.',
                'invalid_choice': 'Invalid product selection. Please choose from available categories.',
            },
            'product_type': {
                'required': 'Product type is required. Please select a product type.',
                'invalid_choice': 'Invalid product type. Please choose Wood or Furniture.',
            },
            'quantity': {
                'required': 'Quantity is required. Please specify how many items to sell.',
                'invalid': 'Please enter a valid number for quantity.',
                'min_value': 'Quantity must be at least 1. Cannot sell zero or negative items.',
                'max_value': 'Quantity is too large. Please check available stock.',
            },
            'unit_price': {
                'required': 'Unit price is required. Please enter the price per item.',
                'invalid': 'Please enter a valid price amount.',
                'min_value': 'Unit price must be greater than 0.',
                'max_digits': 'Price is too large. Please enter a reasonable amount.',
            },
            'total_sales_amount': {
                'invalid': 'Total sales amount calculation error.',
            },
            'date': {
                'required': 'Sale date is required. Please select the date of sale.',
                'invalid': 'Please enter a valid date in the format YYYY-MM-DD.',
            },
            'payment_type': {
                'required': 'Payment method is required. Please select how the customer will pay.',
                'invalid_choice': 'Invalid payment method. Please choose Cash, Cheque, or Bank Overdraft.',
            },
            'sales_agent': {
                'required': 'Sales agent name is required. Please enter who is making this sale.',
                'max_length': 'Sales agent name is too long. Please use 50 characters or less.',
                'invalid': 'Please enter a valid sales agent name.',
            },
        }
        
        # Custom field labels for better clarity
        labels = {
            'customer': 'Customer Full Name',
            'product_name': 'Product Name',
            'product_type': 'Product Type',
            'quantity': 'Quantity to Sell',
            'unit_price': 'Unit Price (UGX)',
            'total_sales_amount': 'Total Sales Amount (UGX)',
            'date': 'Sale Date',
            'payment_type': 'Payment Method',
            'sales_agent': 'Sales Agent Name',
            'transport_required': 'Delivery Required',
        }
        
        # Helpful text to guide users
        help_texts = {
            # customer_name help text is now handled in the field definition above
            'product_name': 'Select the product name being sold (Timber, Sofa, Tables, etc.)',
            'product_type': 'Select whether this is a Wood or Furniture product',
            'quantity': 'Number of items to sell (must be available in stock)',
            'unit_price': 'Price per individual item in Uganda Shillings (UGX)',
            'total_sales_amount': 'Automatically calculated when you enter quantity and unit price',
            'date': 'Date when this sale occurred (cannot be in the future)',
            'payment_type': 'How the customer is paying for this purchase',
            'sales_agent': 'Name of the employee making this sale',
            'transport_required': 'Check if customer needs delivery service (5% transport fee applies)',
        }
        
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'title': 'Sale date cannot be in the future'
            }),
            'quantity': forms.NumberInput(attrs={
                'min': '1', 
                'step': '1',
                'title': 'Quantity must be greater than 0',
                'id': 'id_quantity',
                'onchange': 'calculateTotal()',
                'oninput': 'calculateTotal()'
            }),
            'unit_price': forms.NumberInput(attrs={
                'min': '0',
                'step': '0',
                'title': 'Unit price must be greater than 0',
                'id': 'id_unit_price',
                'onchange': 'calculateTotal()',
                'oninput': 'calculateTotal()'
            }),
            'total_sales_amount': forms.NumberInput(attrs={
                'readonly': 'readonly',
                'id': 'id_total_sales_amount',
                'title': 'This field is automatically calculated',
                'class': 'readonly-field',
                'tabindex': '-1'
            }),
            'transport_required': forms.CheckboxInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # Call the parent class first
        
        # Set max date to today to prevent future dates
        from datetime import date
        self.fields['date'].widget.attrs['max'] = date.today().strftime('%Y-%m-%d')
        
        # Filter product choices to only show products with available stock (consolidated)
        from django.db.models import Sum
        consolidated_stock = Stock.objects.values('product_name', 'product_type').annotate(
            total_quantity=Sum('quantity')
        ).filter(total_quantity__gt=0)
        
        # Get unique product names that have stock
        available_product_names = consolidated_stock.values_list('product_name', flat=True).distinct()
        product_name_choices = [
            (product_name, product_name) for product_name in available_product_names
        ]
        
        # Get unique product types that have stock  
        available_product_types = consolidated_stock.values_list('product_type', flat=True).distinct()
        product_type_choices = [
            (product_type, product_type) for product_type in available_product_types
        ]
        
        # Update field choices to only show available items
        if product_name_choices:
            self.fields['product_name'].widget = forms.Select(choices=[('', 'Select Product Name')] + product_name_choices)
        else:
            self.fields['product_name'].widget = forms.Select(choices=[('', 'No products in stock')])
            
        if product_type_choices:
            self.fields['product_type'].widget = forms.Select(choices=[('', 'Select Product Type')] + product_type_choices)
        else:
            self.fields['product_type'].widget = forms.Select(choices=[('', 'No product types in stock')])
        
        # Create sales agent dropdown from employee list
        from django.contrib.auth.models import User
        employees = User.objects.filter(groups__name="Employee")
        sales_agent_choices = [('', 'Select Sales Agent')]
        for employee in employees:
            # Use full name if available, otherwise username
            display_name = f"{employee.first_name} {employee.last_name}".strip() or employee.username
            sales_agent_choices.append((employee.username, display_name))
        
        # Update sales_agent field to be a dropdown
        self.fields['sales_agent'].widget = forms.Select(choices=sales_agent_choices)
        
        # Add data attributes for JavaScript quantity validation
        self.fields['product_name'].widget.attrs.update({
            'data-stock-info': 'true',
            'onchange': 'updateQuantityLimits()'
        })
        self.fields['product_type'].widget.attrs.update({
            'onchange': 'updateQuantityLimits()'
        })
        
        # Add required attributes for client-side validation
        required_fields = ['customer_name', 'product_name', 'product_type', 'quantity', 'unit_price', 'date', 'payment_type', 'sales_agent']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['required'] = 'required'
        
        # Make total_sales_amount field read-only in the form
        if 'total_sales_amount' in self.fields:
            self.fields['total_sales_amount'].widget.attrs['readonly'] = 'readonly'
        
        # Minimal crispy form setup - all layout handled by templates
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # All styling and layout is now handled by template snippets


class StockForm(forms.ModelForm):
    """
    Stock Form - Creates and edits stock records
    """
    
    # Override supplier field to use dropdown of registered suppliers
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all().order_by('name'),
        empty_label="-- Select Supplier --",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cordes-blue focus:border-transparent',
            'title': 'Select a registered supplier from the dropdown'
        }),
        help_text='Select from registered suppliers. If no suppliers are available, please add a new supplier first.',
        error_messages={
            'required': 'Please select a supplier from the dropdown.',
            'invalid_choice': 'Please select a valid supplier from the list.'
        }
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Update help text based on available suppliers
        if not Supplier.objects.exists():
            self.fields['supplier'].empty_label = "-- No suppliers available. Add a supplier first --"
            self.fields['supplier'].help_text = 'No suppliers are registered yet. Please add a supplier before creating stock entries.'

    
    class Meta:
        model = Stock   # Based on Stock model
        fields = ['product_name', 'product_type', 'quantity', 'date', 'supplier', 'unit_cost', 'total_cost', 'origin']
        # Using separate product_name and product_type fields for better display
        
        # Custom error messages for better user experience
        error_messages = {
            'product_name': {
                'required': 'Product name is required. Please select a product category.',
                'invalid_choice': 'Invalid product selection. Please choose from available categories.',
            },
            'product_type': {
                'required': 'Product type is required. Please select a product type.',
                'invalid_choice': 'Invalid product type. Please choose Wood or Furniture.',
            },
            'quantity': {
                'required': 'Stock quantity is required. Please specify how many items to add.',
                'invalid': 'Please enter a valid number for quantity.',
                'min_value': 'Quantity must be at least 1. Cannot add zero or negative stock.',
                'max_value': 'Quantity is too large. Please enter a reasonable stock amount.',
            },
            'date': {
                'required': 'Stock date is required. Please select when the stock was received.',
                'invalid': 'Please enter a valid date in the format YYYY-MM-DD.',
            },
            # supplier_name errors are now handled in the field definition above
            'unit_cost': {
                'required': 'Unit cost is required. Please enter the cost per item.',
                'invalid': 'Please enter a valid unit cost amount.',
                'min_value': 'Unit cost must be greater than 0.',
                'max_digits': 'Unit cost is too large. Please enter a reasonable amount.',
            },
            'total_cost': {
                'invalid': 'Please enter a valid total cost amount.',
            },
            'origin': {
                'required': 'Origin is required. Please select where this stock came from.',
                'invalid_choice': 'Invalid origin. Please choose Western, Central, or Eastern.',
            },
        }
        
        # Custom field labels for better clarity
        labels = {
            'product_name': 'Product Name',
            'product_type': 'Product Type',
            'quantity': 'Stock Quantity',
            'date': 'Stock Date',
            'supplier': 'Supplier Name',
            'unit_cost': 'Unit Cost (UGX)',
            'total_cost': 'Total Cost (UGX)',
            'origin': 'Origin Region',
        }
        
        # Helpful text to guide users
        help_texts = {
            'product_name': 'Select the product name to add to inventory (Timber, Sofa, Tables, etc.)',
            'product_type': 'Select whether this is a Wood or Furniture product',
            'quantity': 'Number of items to add to stock',
            'date': 'Date when the stock was received (cannot be in the future)',
            # supplier help text is now handled in the field definition above
            'unit_cost': 'Cost per individual item in UGX',
            'total_cost': 'Automatically calculated when you enter quantity and unit cost',
            'origin': 'Region where this stock originated from',
        }
        
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'title': 'Stock date cannot be in the future'
            }),
            'quantity': forms.NumberInput(attrs={
                'min': '1',
                'step': '1',
                'title': 'Quantity must be greater than 0',
                'id': 'id_quantity',
                'onchange': 'calculateStockTotal()',
                'oninput': 'calculateStockTotal()'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'min': '0.01',
                'step': '0.01',
                'title': 'Unit cost must be greater than 0',
                'id': 'id_unit_cost',
                'placeholder': 'e.g., 15000',
                'onchange': 'calculateStockTotal()',
                'oninput': 'calculateStockTotal()'
            }),
            'total_cost': forms.NumberInput(attrs={
                'readonly': 'readonly',
                'id': 'id_total_cost',
                'title': 'This field is automatically calculated',
                'class': 'readonly-field',
                'tabindex': '-1'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set max date to today to prevent future dates
        from datetime import date
        self.fields['date'].widget.attrs['max'] = date.today().strftime('%Y-%m-%d')
        
        # Add required attributes for client-side validation
        required_fields = ['product_name', 'product_type', 'quantity', 'date', 'supplier_name', 'unit_cost', 'origin']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['required'] = 'required'
        
        # Minimal crispy form setup - all layout handled by templates
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # All styling and layout is now handled by template snippets


# Login Form for enhanced validation and error handling
class LoginForm(forms.Form):
    """
    Login Form - Handles user authentication with proper validation
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-cordes-dark focus:border-transparent outline-none transition duration-150 ease-in-out text-lg',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
            'novalidate': 'novalidate'
        }),
        error_messages={
            'required': 'Username is required.',
            'max_length': 'Username cannot exceed 150 characters.'
        }
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-cordes-dark focus:border-transparent outline-none transition duration-150 ease-in-out text-lg',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        }),
        error_messages={
            'required': 'Password is required.'
        }
    )
    
    ROLE_CHOICES = [
        ('', 'Select your role'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-cordes-dark focus:border-transparent outline-none transition duration-150 ease-in-out text-lg'
        }),
        error_messages={
            'required': 'Please select your role.',
            'invalid_choice': 'Please select a valid role.'
        }
    )


class CustomerForm(forms.ModelForm):
    """
    Customer Form - Creates and edits customer records
    """
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        
        error_messages = {
            'name': {
                'required': 'Customer name is required.',
                'unique': 'A customer with this name already exists.',
                'max_length': 'Customer name is too long. Please use 100 characters or less.',
            },
            'phone': {
                'max_length': 'Phone number is too long. Please use 15 characters or less.',
            },
            'email': {
                'invalid': 'Please enter a valid email address.',
            },
        }
        
        labels = {
            'name': 'Customer Name',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'address': 'Physical Address',
        }
        
        help_texts = {
            'name': 'Enter the customer\'s full name',
            'phone': 'Customer\'s contact phone number (optional)',
            'email': 'Customer\'s email address (optional)',
            'address': 'Customer\'s physical address (optional)',
        }
        
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., John Mukasa',
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'e.g., +256 700 123 456',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'e.g., john@example.com',
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'e.g., Plot 123, Kampala Road, Kampala',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add required attribute for name field
        self.fields['name'].widget.attrs['required'] = 'required'
        
        # Setup crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'


class SupplierForm(forms.ModelForm):
    """
    Supplier Form - Creates and edits supplier records
    """
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        
        error_messages = {
            'name': {
                'required': 'Supplier name is required.',
                'unique': 'A supplier with this name already exists.',
                'max_length': 'Supplier name is too long. Please use 100 characters or less.',
            },
            'contact_person': {
                'max_length': 'Contact person name is too long. Please use 100 characters or less.',
            },
            'phone': {
                'max_length': 'Phone number is too long. Please use 15 characters or less.',
            },
            'email': {
                'invalid': 'Please enter a valid email address.',
            },
        }
        
        labels = {
            'name': 'Supplier Company Name',
            'contact_person': 'Contact Person',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'address': 'Physical Address',
        }
        
        help_texts = {
            'name': 'Enter the supplier company name',
            'contact_person': 'Primary contact person at the supplier',
            'phone': 'Supplier\'s contact phone number',
            'email': 'Supplier\'s email address',
            'address': 'Supplier\'s physical address',
        }
        
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., Mbawo Timberworks',
                'class': 'form-control'
            }),
            'contact_person': forms.TextInput(attrs={
                'placeholder': 'e.g., David Mbawo',
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'e.g., +256 700 123 456',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'e.g., info@mbawo.com',
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'e.g., Industrial Area, Kampala',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add required attribute for name field
        self.fields['name'].widget.attrs['required'] = 'required'
        
        # Setup crispy forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'

