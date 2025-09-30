"""
MAYONDO FURNITURE MANAGEMENT SYSTEM - FORMS
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
from .models import Sale, Stock   # Import the database models (Sale and Stock)

# Crispy forms imports for professional styling
from crispy_forms.helper import FormHelper   # Crispy helper to control form look & feel
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML, Div   # Tools for layout
from crispy_forms.bootstrap import FormActions   # Extra Bootstrap actions (optional)


class SaleForm(forms.ModelForm):
    """
    Sale Form - Creates and edits sales records
    Features professional styling with Tailwind CSS integration
    Includes validation and user-friendly field layouts
    """
    class Meta:
        model = Sale   # This form is based on the Sale model
        fields = ['customer_name', 'product_name', 'product_type', 
                 'quantity', 'date', 'payment_type', 'sales_agent', 'transport_required']
        # These are the fields from the model that will appear in the form
        
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  # Render date field as HTML date picker
            'transport_required': forms.CheckboxInput(),      # Render transport_required as checkbox
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   # Call the parent class first
        
        # Crispy form helper for layout & styling
        self.helper = FormHelper()
        self.helper.form_method = 'post'         # Form will submit using POST
        self.helper.form_class = 'form-horizontal'  # Use horizontal form layout
        self.helper.label_class = 'col-lg-3 col-md-4 col-sm-5 col-12'   # Label width
        self.helper.field_class = 'col-lg-9 col-md-8 col-sm-7 col-12'   # Field width
        
        # Define the actual layout of the form
        self.helper.layout = Layout(
            # Card container
            HTML('<div class="bg-white p-6 rounded-lg shadow-sm">'),
            HTML('<h2 class="text-2xl font-bold text-gray-800 mb-6">Sale Information</h2>'),
            
            # Info box
            HTML('<div class="mb-4 p-3 bg-blue-50 rounded border-l-4 border-blue-400">'),
            HTML('<p class="text-sm text-blue-700"><i class="fas fa-info-circle mr-2"></i>'
                 '<strong>Note:</strong> Product ID will be automatically generated when you save this sale.</p>'),
            HTML('</div>'),
            
            # Customer name (full row)
            Row(
                Column('customer_name', css_class='form-group col-md-12 mb-4'),
                css_class='form-row'
            ),
            
            # Product name + type side by side
            Row(
                Column('product_name', css_class='form-group col-md-6 mb-4'),
                Column('product_type', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            # Quantity, Date, Payment type (3 columns)
            Row(
                Column('quantity', css_class='form-group col-md-4 mb-4'),
                Column('date', css_class='form-group col-md-4 mb-4'),
                Column('payment_type', css_class='form-group col-md-4 mb-4'),
                css_class='form-row'
            ),
            
            # Sales agent + Transport required (checkbox)
            Row(
                Column('sales_agent', css_class='form-group col-md-8 mb-4'),
                Column(
                    Field('transport_required', wrapper_class='d-flex align-items-center h-100'), 
                    css_class='form-group col-md-4 mb-4'
                ),
                css_class='form-row'
            ),
            
            # Form actions (buttons)
            HTML('<div class="form-actions mt-4">'),
            Submit('submit', 'Save Sale', css_class='btn bg-cordes-dark text-white px-6 py-3 '
                                                   'rounded-lg hover:bg-cordes-blue transition-colors mr-3'),
            HTML('<a href="/saleRecord/" class="btn bg-gray-500 text-white px-6 py-3 rounded-lg '
                 'hover:bg-gray-600 transition-colors">Cancel</a>'),
            HTML('</div>'),
            HTML('</div>')
        )


class StockForm(forms.ModelForm):
    """
    Stock Form - Creates and edits stock records
    """
    class Meta:
        model = Stock   # Based on Stock model
        fields = ['product_name', 'product_type', 'quantity', 
                 'date', 'supplier_name', 'cost', 'price', 'origin']
        # These fields will appear in the stock form
        
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  # Date picker widget
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Crispy form helper setup
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3 col-md-4 col-sm-5 col-12'
        self.helper.field_class = 'col-lg-9 col-md-8 col-sm-7 col-12'
        
        # Layout for stock form
        self.helper.layout = Layout(
            HTML('<div class="bg-white p-6 rounded-lg shadow-sm">'),
            HTML('<h2 class="text-2xl font-bold text-gray-800 mb-6">Stock Information</h2>'),
            
            # Info box
            HTML('<div class="mb-4 p-3 bg-green-50 rounded border-l-4 border-green-400">'),
            HTML('<p class="text-sm text-green-700"><i class="fas fa-info-circle mr-2"></i>'
                 '<strong>Note:</strong> Product ID will be automatically generated based on category and date.</p>'),
            HTML('</div>'),
            
            # Product name + type
            Row(
                Column('product_name', css_class='form-group col-md-6 mb-4'),
                Column('product_type', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            # Quantity + Date
            Row(
                Column('quantity', css_class='form-group col-md-4 mb-4'),
                Column('date', css_class='form-group col-md-8 mb-4'),
                css_class='form-row'
            ),
            
            # Supplier
            Row(
                Column('supplier_name', css_class='form-group col-md-12 mb-4'),
                css_class='form-row'
            ),
            
            # Cost, Price, Origin
            Row(
                Column('cost', css_class='form-group col-md-4 mb-4'),
                Column('price', css_class='form-group col-md-4 mb-4'),
                Column('origin', css_class='form-group col-md-4 mb-4'),
                css_class='form-row'
            ),
            
            # Form actions
            HTML('<div class="form-actions mt-4">'),
            Submit('submit', 'Save Stock', css_class='btn bg-cordes-dark text-white px-6 py-3 '
                                                    'rounded-lg hover:bg-cordes-blue transition-colors mr-3'),
            HTML('<a href="/stockRecord/" class="btn bg-gray-500 text-white px-6 py-3 rounded-lg '
                 'hover:bg-gray-600 transition-colors">Cancel</a>'),
            HTML('</div>'),
            HTML('</div>')
        )


# Read-only form for viewing records
class SaleViewForm(SaleForm):
    """
    Sale View Form - Read-only version of SaleForm
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make all fields read-only (cannot edit)
        for field in self.fields:
            self.fields[field].widget.attrs['readonly'] = True
            self.fields[field].widget.attrs['disabled'] = True
        
        # New layout for viewing (details only, no save button)
        self.helper.layout = Layout(
            HTML('<div class="bg-white p-6 rounded-lg shadow-sm">'),
            HTML('<h2 class="text-2xl font-bold text-gray-800 mb-6">Sale Details</h2>'),
            
            # Product ID + Customer
            Row(
                Column('product_id', css_class='form-group col-md-6 mb-4'),
                Column('customer_name', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            # Product name + type
            Row(
                Column('product_name', css_class='form-group col-md-6 mb-4'),
                Column('product_type', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            # Quantity, Date, Payment type
            Row(
                Column('quantity', css_class='form-group col-md-4 mb-4'),
                Column('date', css_class='form-group col-md-4 mb-4'),
                Column('payment_type', css_class='form-group col-md-4 mb-4'),
                css_class='form-row'
            ),
            
            # Sales agent + transport
            Row(
                Column('sales_agent', css_class='form-group col-md-8 mb-4'),
                Column('transport_required', css_class='form-group col-md-4 mb-4'),
                css_class='form-row'
            ),
            
            # Actions: Edit or Back
            HTML('<div class="form-actions mt-4">'),
            HTML('<a href="/edit/{{ object.id }}" class="btn bg-blue-600 text-white px-6 py-3 '
                 'rounded-lg hover:bg-blue-700 transition-colors mr-3">Edit</a>'),
            HTML('<a href="/saleRecord/" class="btn bg-gray-500 text-white px-6 py-3 rounded-lg '
                 'hover:bg-gray-600 transition-colors">Back to List</a>'),
            HTML('</div>'),
            HTML('</div>')
        )


class StockViewForm(StockForm):
    """
    Stock View Form - Read-only version of StockForm
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make all fields read-only
        for field in self.fields:
            self.fields[field].widget.attrs['readonly'] = True
            self.fields[field].widget.attrs['disabled'] = True
        
        # Layout for viewing stock
        self.helper.layout = Layout(
            HTML('<div class="bg-white p-6 rounded-lg shadow-sm">'),
            HTML('<h2 class="text-2xl font-bold text-gray-800 mb-6">Stock Details</h2>'),
            
            # Product ID + Product name
            Row(
                Column('product_id', css_class='form-group col-md-6 mb-4'),
                Column('product_name', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            # Product type + quantity
            Row(
                Column('product_type', css_class='form-group col-md-6 mb-4'),
                Column('quantity', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            # Date + Supplier
            Row(
                Column('date', css_class='form-group col-md-4 mb-4'),
                Column('supplier_name', css_class='form-group col-md-8 mb-4'),
                css_class='form-row'
            ),
            
            # Cost, Price, Origin
            Row(
                Column('cost', css_class='form-group col-md-4 mb-4'),
                Column('price', css_class='form-group col-md-4 mb-4'),
                Column('origin', css_class='form-group col-md-4 mb-4'),
                css_class='form-row'
            ),
            
            # Actions: Edit or Back
            HTML('<div class="form-actions mt-4">'),
            HTML('<a href="/edit/{{ object.id }}" class="btn bg-blue-600 text-white px-6 py-3 '
                 'rounded-lg hover:bg-blue-700 transition-colors mr-3">Edit</a>'),
            HTML('<a href="/stockRecord/" class="btn bg-gray-500 text-white px-6 py-3 rounded-lg '
                 'hover:bg-gray-600 transition-colors">Back to List</a>'),
            HTML('</div>'),
            HTML('</div>')
        )
