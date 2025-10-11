from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Sale, Stock, Customer, Supplier
from django.db.models import Q

@require_GET
def search_dashboard(request):
    query = request.GET.get('q', '').strip()
    sales_results = []
    stock_results = []
    customer_results = []
    supplier_results = []
    
    if query:
        # Search in Sales
        sales = Sale.objects.select_related('customer').filter(
            Q(product_id__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(product_name__icontains=query) |
            Q(product_type__icontains=query) |
            Q(sales_agent__icontains=query)
        )
        
        # Search in Stock
        stock = Stock.objects.select_related('supplier').filter(
            Q(product_id__icontains=query) |
            Q(product_name__icontains=query) |
            Q(product_type__icontains=query) |
            Q(supplier__name__icontains=query)
        )
        
        # Search in Customers
        customers = Customer.objects.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query) |
            Q(address__icontains=query)
        )
        
        # Search in Suppliers
        suppliers = Supplier.objects.filter(
            Q(name__icontains=query) |
            Q(contact_person__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query) |
            Q(address__icontains=query)
        )
        
        sales_results = []
        for sale in sales:
            sale_data = {
                'id': sale.id,
                'product_id': sale.product_id,
                'customer_name': sale.customer.name if sale.customer else 'N/A',
                'product_name': sale.product_name,
                'product_type': sale.product_type,
                'quantity': sale.quantity,
                'sales_agent': sale.sales_agent,
                'date': sale.date.strftime('%Y-%m-%d') if sale.date else None,
            }
            sales_results.append(sale_data)
            
        stock_results = []
        for stock_item in stock:
            stock_data = {
                'id': stock_item.id,
                'product_id': stock_item.product_id,
                'product_name': stock_item.product_name,
                'product_type': stock_item.product_type,
                'quantity': stock_item.quantity,
                'supplier_name': stock_item.supplier.name if stock_item.supplier else 'N/A',
                'date': stock_item.date.strftime('%Y-%m-%d') if stock_item.date else None,
            }
            stock_results.append(stock_data)
            
        customer_results = list(customers.values())
        supplier_results = list(suppliers.values())
    
    return JsonResponse({
        'sales': sales_results,
        'stock': stock_results,
        'customers': customer_results,
        'suppliers': supplier_results
    })
