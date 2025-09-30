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
from django import forms

# Local imports
from .models import Sale, Stock

# Crispy forms imports for professional styling
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML, Div
from crispy_forms.bootstrap import FormActions


class SaleForm(forms.ModelForm):
    """
    Sale Form - Creates and edits sales records
    Features professional styling with Tailwind CSS integration
    Includes validation and user-friendly field layouts
    """
    class Meta:
        model = Sale
        fields = ['customer_name', 'product_name', 'product_type', 
                 'quantity', 'date', 'payment_type', 'sales_agent', 'transport_required']
        
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'transport_required': forms.CheckboxInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3 col-md-4 col-sm-5 col-12'
        self.helper.field_class = 'col-lg-9 col-md-8 col-sm-7 col-12'
        
        self.helper.layout = Layout(
            HTML('<div class="bg-white p-6 rounded-lg shadow-sm">'),
            HTML('<h2 class="text-2xl font-bold text-gray-800 mb-6">Sale Information</h2>'),
            
            HTML('<div class="mb-4 p-3 bg-blue-50 rounded border-l-4 border-blue-400">'),
            HTML('<p class="text-sm text-blue-700"><i class="fas fa-info-circle mr-2"></i><strong>Note:</strong> Product ID will be automatically generated when you save this sale.</p>'),
            HTML('</div>'),
            
            Row(
                Column('customer_name', css_class='form-group col-md-12 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('product_name', css_class='form-group col-md-6 mb-4'),
                Column('product_type', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('quantity', css_class='form-group col-md-4 mb-4'),
                Column('date', css_class='form-group col-md-4 mb-4'),
                Column('payment_type', css_class='form-group col-md-4 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('sales_agent', css_class='form-group col-md-8 mb-4'),
                Column(
                    Field('transport_required', wrapper_class='d-flex align-items-center h-100'), 
                    css_class='form-group col-md-4 mb-4'
                ),
                css_class='form-row'
            ),
            
            HTML('<div class="form-actions mt-4">'),
            Submit('submit', 'Save Sale', css_class='btn bg-cordes-dark text-white px-6 py-3 rounded-lg hover:bg-cordes-blue transition-colors mr-3'),
            HTML('<a href="/saleRecord/" class="btn bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors">Cancel</a>'),
            HTML('</div>'),
            HTML('</div>')
        )


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['product_name', 'product_type', 'quantity', 
                 'date', 'supplier_name', 'cost', 'price', 'origin']
        
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3 col-md-4 col-sm-5 col-12'
        self.helper.field_class = 'col-lg-9 col-md-8 col-sm-7 col-12'
        
        self.helper.layout = Layout(
            HTML('<div class="bg-white p-6 rounded-lg shadow-sm">'),
            HTML('<h2 class="text-2xl font-bold text-gray-800 mb-6">Stock Information</h2>'),
            
            HTML('<div class="mb-4 p-3 bg-green-50 rounded border-l-4 border-green-400">'),
            HTML('<p class="text-sm text-green-700"><i class="fas fa-info-circle mr-2"></i><strong>Note:</strong> Product ID will be automatically generated based on category and date.</p>'),
            HTML('</div>'),
            
            Row(
                Column('product_name', css_class='form-group col-md-6 mb-4'),
                Column('product_type', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('quantity', css_class='form-group col-md-4 mb-4'),
                Column('date', css_class='form-group col-md-8 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('supplier_name', css_class='form-group col-md-12 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('cost', css_class='form-group col-md-4 mb-4'),
                Column('price', css_class='form-group col-md-4 mb-4'),
                Column('origin', css_class='form-group col-md-4 mb-4'),
                css_class='form-row'
            ),
            
            HTML('<div class="form-actions mt-4">'),
            Submit('submit', 'Save Stock', css_class='btn bg-cordes-dark text-white px-6 py-3 rounded-lg hover:bg-cordes-blue transition-colors mr-3'),
            HTML('<a href="/stockRecord/" class="btn bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors">Cancel</a>'),
            HTML('</div>'),
            HTML('</div>')
        )


# Read-only form for viewing records
class SaleViewForm(SaleForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make all fields read-only
        for field in self.fields:
            self.fields[field].widget.attrs['readonly'] = True
            self.fields[field].widget.attrs['disabled'] = True
        
        # Update layout for view mode
        self.helper.layout = Layout(
            HTML('<div class="bg-white p-6 rounded-lg shadow-sm">'),
            HTML('<h2 class="text-2xl font-bold text-gray-800 mb-6">Sale Details</h2>'),
            
            Row(
                Column('product_id', css_class='form-group col-md-6 mb-4'),
                Column('customer_name', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('product_name', css_class='form-group col-md-6 mb-4'),
                Column('product_type', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('quantity', css_class='form-group col-md-4 mb-4'),
                Column('date', css_class='form-group col-md-4 mb-4'),
                Column('payment_type', css_class='form-group col-md-4 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('sales_agent', css_class='form-group col-md-8 mb-4'),
                Column('transport_required', css_class='form-group col-md-4 mb-4'),
                css_class='form-row'
            ),
            
            HTML('<div class="form-actions mt-4">'),
            HTML('<a href="/edit/{{ object.id }}" class="btn bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors mr-3">Edit</a>'),
            HTML('<a href="/saleRecord/" class="btn bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors">Back to List</a>'),
            HTML('</div>'),
            HTML('</div>')
        )


class StockViewForm(StockForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make all fields read-only
        for field in self.fields:
            self.fields[field].widget.attrs['readonly'] = True
            self.fields[field].widget.attrs['disabled'] = True
        
        # Update layout for view mode
        self.helper.layout = Layout(
            HTML('<div class="bg-white p-6 rounded-lg shadow-sm">'),
            HTML('<h2 class="text-2xl font-bold text-gray-800 mb-6">Stock Details</h2>'),
            
            Row(
                Column('product_id', css_class='form-group col-md-6 mb-4'),
                Column('product_name', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('product_type', css_class='form-group col-md-6 mb-4'),
                Column('quantity', css_class='form-group col-md-6 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('date', css_class='form-group col-md-4 mb-4'),
                Column('supplier_name', css_class='form-group col-md-8 mb-4'),
                css_class='form-row'
            ),
            
            Row(
                Column('cost', css_class='form-group col-md-4 mb-4'),
                Column('price', css_class='form-group col-md-4 mb-4'),
                Column('origin', css_class='form-group col-md-4 mb-4'),
                css_class='form-row'
            ),
            
            HTML('<div class="form-actions mt-4">'),
            HTML('<a href="/edit/{{ object.id }}" class="btn bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors mr-3">Edit</a>'),
            HTML('<a href="/stockRecord/" class="btn bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition-colors">Back to List</a>'),
            HTML('</div>'),
            HTML('</div>')
        )
