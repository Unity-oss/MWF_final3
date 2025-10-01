from django.contrib import admin
from .models import Product, Sale, Stock, Notification

# Register Product model for admin management
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_type', 'description', 'created_at']
    list_filter = ['product_type', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name', 'product_type']

# Register other models (optional - for better admin experience)
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'customer_name', 'product_ref', 'quantity', 'date', 'sales_agent']
    list_filter = ['date', 'payment_type', 'transport_required']
    search_fields = ['customer_name', 'product_id']

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'product_ref', 'quantity', 'date', 'supplier_name']
    list_filter = ['date', 'origin']
    search_fields = ['product_id', 'supplier_name']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'activity_type', 'is_read', 'created_at']
    list_filter = ['activity_type', 'is_read', 'created_at']
