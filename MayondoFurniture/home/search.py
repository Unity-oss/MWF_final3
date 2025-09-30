from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Sale, Stock
from django.db.models import Q

@require_GET
def search_dashboard(request):
    query = request.GET.get('q', '').strip()
    sales_results = []
    stock_results = []
    if query:
        sales = Sale.objects.filter(
            Q(product_id__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(product_name__icontains=query) |
            Q(product_type__icontains=query) |
            Q(sales_agent__icontains=query)
        )
        stock = Stock.objects.filter(
            Q(product_id__icontains=query) |
            Q(product_name__icontains=query) |
            Q(product_type__icontains=query) |
            Q(supplier_name__icontains=query)
        )
        sales_results = list(sales.values())
        stock_results = list(stock.values())
    return JsonResponse({
        'sales': sales_results,
        'stock': stock_results
    })
