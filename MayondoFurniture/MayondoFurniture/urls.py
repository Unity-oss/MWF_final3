"""
MAYONDO FURNITURE    # Import all view functions from the home app
from home.views import landingPage, loginPage, logoutPage, dashBoard, addSale, saleRecord, viewSingleSale,editSale,updateSale,deleteSale, saleReport,stockRecord, stockReport, report, addStock, addUser,activityFeed, notifications, sales_report, stock_report, viewSingleStock, editStock, updateStock, deleteStock, mark_notification_read, generateReceiptANAGEMENT SYSTEM - URL CONFIGURATION
=======================================================

This file defines all the URL patterns for the application, mapping URLs to their
corresponding view functions.

URL Structure:
- Authentication: login, logout, landing page
- Dashboard: main dashboard with statistics
- Sales Management: add, view, edit, delete sales records
- Stock Management: add, view, edit, delete inventory items
- Reports: various business reports
- User Management: add users (managers only)
- API endpoints: notifications, search, activity feed

Dynamic URLs use parameters like <str:product_id> for CRUD operations
"""

from django.contrib import admin
from django.urls import path

# Import all view functions from the home app
from home.views import (
    landingPage, loginPage, logoutPage, dashBoard, addSale, saleRecord, 
    viewSingleSale, editSale, updateSale, deleteSale, saleReport, stockRecord, 
    stockReport, report, addStock, addUser, activityFeed, notifications, 
    sales_report, stock_report, viewSingleStock, editStock, updateStock, 
    deleteStock, mark_notification_read, mark_all_notifications_read, generateReceipt
)
from home.search import search_dashboard

urlpatterns = [
    # ===== DJANGO ADMIN =====
    path('admin/', admin.site.urls),
    
    # ===== AUTHENTICATION & MAIN PAGES =====
    path('', landingPage),                          # Home/Landing page
    path('login/', loginPage, name='login'),        # User login
    path('logout/', logoutPage, name='logout'),     # User logout
    path('dashboard/', dashBoard, name='dashboard'), # Main dashboard
    
    # ===== USER MANAGEMENT =====
    path('addUser/', addUser, name='addUser'),      # Add new users (managers only)
    
    # ===== SALES MANAGEMENT =====
    path('addSale/', addSale, name='addSale'),              # Create new sale
    path('saleRecord/', saleRecord, name='saleRecord'),     # View all sales
    path('saleReport/', saleReport, name='saleReport'),     # Sales report page
    path('sales_report/', sales_report, name='sales_report'), # Alternative sales report
    
    # ===== STOCK/INVENTORY MANAGEMENT =====
    path('addStock/', addStock, name='addStock'),           # Add new inventory
    path('stockRecord/', stockRecord, name='stockRecord'), # View all stock
    path('stockReport/', stockReport, name='stockReport'), # Stock report page
    path('stock_report/', stock_report, name='stock_report'), # Alternative stock report
    
    # ===== REPORTING SYSTEM =====
    path('report/', report, name='report'),         # General report generator
    
    # ===== NOTIFICATIONS & ACTIVITY =====
    path("notifications/", notifications, name='notifications'),     # User notifications
    path("activityFeed/", activityFeed, name='activityFeed'),       # Activity feed
    path('mark_notification_read/', mark_notification_read, name='mark_notification_read'), # Mark single notification as read
    path('mark_all_notifications_read/', mark_all_notifications_read, name='mark_all_notifications_read'), # Mark all notifications as read
    
    # ===== SEARCH FUNCTIONALITY =====
    path('search_dashboard/', search_dashboard, name='search_dashboard'), # Dashboard search

    # ===== DYNAMIC URLS - SALES CRUD OPERATIONS =====
    path('view/<str:product_id>/', viewSingleSale, name='view_sale'),     # View individual sale
    path('edit/<str:product_id>/', editSale, name='edit_sale'),           # Edit sale form
    path('update/<str:product_id>/', updateSale, name='update_sale'),     # Update sale (POST)
    path('delete/<str:product_id>/', deleteSale, name='delete_sale'),     # Delete sale
    path('receipt/<str:product_id>/', generateReceipt, name='generate_receipt'), # Generate receipt
    
    # ===== DYNAMIC URLS - STOCK CRUD OPERATIONS =====
    path('viewStock/<str:product_id>/', viewSingleStock, name='view_stock'),    # View individual stock item
    path('editStock/<str:product_id>/', editStock, name='edit_stock'),          # Edit stock form  
    path('updateStock/<str:product_id>/', updateStock, name='update_stock'),    # Update stock (POST)
    path('deleteStock/<str:product_id>/', deleteStock, name='delete_stock')     # Delete stock item
]

