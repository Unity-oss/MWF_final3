# Add these imports to your existing views.py
from .forms import SaleForm, StockForm, SaleViewForm, StockViewForm
from django.shortcuts import get_object_or_404
from .models import Sale, Stock
from django.contrib import messages
from django.shortcuts import render, redirect
# Example view functions using crispy forms

def edit_stock(request, id):
    """Edit stock record using crispy forms"""
    stock = get_object_or_404(Stock, id=id)
    
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock updated successfully!')
            return redirect('stock_list')  # Redirect to your stock list view
    else:
        form = StockForm(instance=stock)
    
    return render(request, 'edit_stock_new.html', {'form': form, 'stock': stock})


def view_stock(request, id):
    """View stock record using crispy forms"""
    stock = get_object_or_404(Stock, id=id)
    form = StockViewForm(instance=stock)
    
    return render(request, 'view_stock_new.html', {'form': form, 'stock': stock})


def edit_sale(request, id):
    """Edit sale record using crispy forms"""
    sale = get_object_or_404(Sale, id=id)
    
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sale updated successfully!')
            return redirect('sale_list')  # Redirect to your sale list view
    else:
        form = SaleForm(instance=sale)
    
    return render(request, 'edit_sale_new.html', {'form': form, 'sale': sale})


def view_sale(request, id):
    """View sale record using crispy forms"""
    sale = get_object_or_404(Sale, id=id)
    form = SaleViewForm(instance=sale)
    
    return render(request, 'view_sale_new.html', {'form': form, 'sale': sale})


def add_stock(request):
    """Add new stock record using crispy forms"""
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock added successfully!')
            return redirect('stock_list')
    else:
        form = StockForm()
    
    return render(request, 'add_stock_new.html', {'form': form})


def add_sale(request):
    """Add new sale record using crispy forms"""
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sale added successfully!')
            return redirect('sale_list')
    else:
        form = SaleForm()
    
    return render(request, 'add_sale_new.html', {'form': form})