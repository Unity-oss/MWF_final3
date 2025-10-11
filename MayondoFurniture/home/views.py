"""
MAYONDO FURNITURE MANAGEMENT SYSTEM - VIEWS
==================================================

This file contains ALL the view functions that handle user requests and responses
for the Mayondo Furniture Management System. All views are consolidated here
for better maintainability and organization.

Main Features:
- User authentication (login/logout) 
- Dashboard with real-time statistics
- Sales management (CRUD operations)
- Stock management (CRUD operations)  
- Reporting system with role-based access
- User management for managers
- Notification system
- Foreign key relationships for better performance
- Proper Django authentication with @login_required

Note: Previously had views_crispy.py but consolidated everything here for cleaner architecture.
"""

# Django core imports
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache, cache_control
from django.views.decorators.csrf import csrf_protect
from functools import wraps
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse
from functools import wraps
from datetime import datetime

# Local application imports
from home.models import Sale, Stock, Notification, Customer, Supplier
from .forms import SaleForm, StockForm, LoginForm, CustomerForm, SupplierForm

# ===== SECURITY DECORATORS =====
# Decorator to restrict access to managers only
def manager_required(view_func):
    """
    Security decorator to restrict access to managers only
    Redirects to dashboard if user is not a manager
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.groups.filter(name="Manager").exists():
            messages.error(request, "Access denied. Manager privileges required.")
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# IMPROVED: Use Django's built-in authentication instead of referer checking
from django.contrib.auth.decorators import login_required, user_passes_test

# Helper functions for role-based access
def is_employee_or_manager(user):
    """Check if user is authenticated and in Employee or Manager group"""
    return user.is_authenticated and user.groups.filter(name__in=['Manager', 'Employee']).exists()

def is_manager_only(user):
    """Check if user is authenticated and in Manager group only"""
    return user.is_authenticated and user.groups.filter(name='Manager').exists()


def secure_view(view_func):
    """
    Decorator that combines authentication and cache control
    Prevents back button access after logout
    """
    @wraps(view_func)
    @never_cache
    @cache_control(no_cache=True, must_revalidate=True, no_store=True)
    def wrapper(request, *args, **kwargs):
        # Add security headers to response
        response = view_func(request, *args, **kwargs)
        
        # Ensure response has proper headers to prevent caching
        if hasattr(response, '__setitem__'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['X-Frame-Options'] = 'DENY'  # Prevent clickjacking
            
        return response
    return wrapper


# DEPRECATED: Old referer checking (keeping for reference)
# This approach was unreliable and has been replaced with @login_required
def restrict_direct_access_OLD(view_func):
    """
    DEPRECATED: This decorator used unreliable referer checking
    Use @login_required instead for proper authentication
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # This approach was problematic because:
        # - HTTP_REFERER can be spoofed or missing
        # - Breaks legitimate bookmarks/direct links
        # - Not reliable across different browsers
        return view_func(request, *args, **kwargs)
    return _wrapped_view






# ===== MAIN APPLICATION VIEWS =====

def landingPage(request):
    """
    Landing Page View - First page users see when visiting the site
    Displays the main welcome page with system introduction
    """
    return render(request, "index.html")



def loginPage(request):
    """
    Login Page View - Handles user authentication using LoginForm
    Supports role-based login (Manager/Employee) with group verification
    Redirects to dashboard on successful login, shows form errors on failure
    """
    if request.method == "POST":
        print("DEBUG: POST request received")
        form = LoginForm(request.POST)
        print(f"DEBUG: Form created with data: {request.POST}")
        
        if form.is_valid():
            print("DEBUG: Form is valid")
            # Get cleaned data from form
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']

            # Attempt to authenticate user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if user account is active
                if not user.is_active:
                    form.add_error(None, "Your account has been deactivated. Please contact an administrator.")
                    return render(request, "login.html", {'form': form})
                
                # Verify user belongs to the selected role group
                if user.groups.filter(name=role).exists():
                    login(request, user)  # Start user session
                    # Only show welcome message once per login session
                    if not request.session.get('welcome_shown', False):
                        messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                        request.session['welcome_shown'] = True
                    return redirect("dashboard")  # Successful login - go to dashboard
                else:
                    form.add_error('role', f"Access denied. You are not authorized for the '{role}' role. Please check your role selection or contact an administrator.")
                    return render(request, "login.html", {'form': form})
            else:
                # Check if username exists to provide more specific error
                from django.contrib.auth.models import User
                try:
                    existing_user = User.objects.get(username=username)
                    form.add_error('password', "Incorrect password. Please try again or contact an administrator if you've forgotten your password.")
                except User.DoesNotExist:
                    form.add_error('username', "Username not found. Please check your username or contact an administrator for account registration.")
                
                return render(request, "login.html", {'form': form})
        else:
            # Form validation failed - render form with errors
            print(f"DEBUG: Form validation failed. Errors: {form.errors}")
            return render(request, "login.html", {'form': form})
    else:
        # GET request - display empty login form
        print("DEBUG: GET request - creating empty form")
        form = LoginForm()

    print("DEBUG: Rendering template with form")
    return render(request, "login.html", {'form': form})


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutPage(request):
    """
    Secure Logout View - Handles user logout with proper cache control
    Prevents browser back button access after logout
    """
    # Terminate user session completely
    logout(request)
    
    # Clear all session data
    request.session.flush()
    
    # Add security message
    messages.success(request, 'You have been logged out successfully.')
    
    # Create response with strict cache control headers
    response = render(request, "logout.html")
    
    # Prevent caching of any authenticated pages
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response



def create_low_stock_notifications():
    """
    Create notifications for low stock items (< 5 units)
    Only creates new notifications to avoid spam
    """
    try:
        from datetime import datetime, timedelta
        from django.db.models import Q
        
        # Get items with low stock (less than 5 units)
        low_stock_items = Stock.objects.filter(quantity__gt=0, quantity__lt=5)
        
        # Get all managers to notify
        managers = User.objects.filter(groups__name="Manager")
        
        # Check each low stock item
        for item in low_stock_items:
            notification_message = f"⚠️ LOW STOCK ALERT: {item.product_name} ({item.product_type}) - Only {item.quantity} units remaining"
            
            # Check if we already sent a similar notification in the last 24 hours
            last_24_hours = datetime.now() - timedelta(hours=24)
            
            for manager in managers:
                # Check for existing low stock notifications for this specific item
                existing_notification = Notification.objects.filter(
                    Q(user=manager) &
                    Q(message__icontains="LOW STOCK ALERT") &
                    Q(message__icontains=f"{item.product_name} ({item.product_type})") &
                    Q(created_at__gte=last_24_hours)
                ).exists()
                
                # Only create notification if we haven't already notified about this item recently
                if not existing_notification:
                    Notification.objects.create(
                        user=manager,
                        message=notification_message,
                        activity_type="warning"
                    )
    except Exception as e:
        # Fail silently to avoid breaking the dashboard
        print(f"Error creating low stock notifications: {e}")

def create_low_stock_notifications_consolidated(low_stock_products):
    """
    Create notifications for low stock items based on consolidated data
    Clears old notifications when stock is replenished
    """
    try:
        from datetime import datetime, timedelta
        from django.db.models import Q
        
        # Get all managers to notify
        managers = User.objects.filter(groups__name="Manager")
        
        # Get all product combinations that currently exist
        from django.db.models import Sum
        all_products = Stock.objects.values('product_name', 'product_type').annotate(
            total_quantity=Sum('quantity')
        )
        
        for manager in managers:
            # Clear old low stock notifications for items that are now adequately stocked
            for product in all_products:
                if product['total_quantity'] >= 5:  # No longer low stock
                    # Remove old low stock notifications for this product
                    old_notifications = Notification.objects.filter(
                        Q(user=manager) &
                        Q(message__icontains="LOW STOCK ALERT") &
                        Q(message__icontains=f"{product['product_name']} ({product['product_type']})")
                    )
                    deleted_count = old_notifications.count()
                    old_notifications.delete()
                    
                    if deleted_count > 0:
                        # Create a restocked notification
                        Notification.objects.create(
                            user=manager,
                            message=f"✅ RESTOCKED: {product['product_name']} ({product['product_type']}) - Now {product['total_quantity']} units available",
                            activity_type="success"
                        )
        
        # Create new low stock notifications only for items still low
        last_24_hours = datetime.now() - timedelta(hours=24)
        
        for product in low_stock_products:
            notification_message = f"⚠️ LOW STOCK ALERT: {product['product_name']} ({product['product_type']}) - Only {product['total_quantity']} units remaining"
            
            for manager in managers:
                # Check if we already sent a similar notification in the last 24 hours
                existing_notification = Notification.objects.filter(
                    Q(user=manager) &
                    Q(message__icontains="LOW STOCK ALERT") &
                    Q(message__icontains=f"{product['product_name']} ({product['product_type']})") &
                    Q(created_at__gte=last_24_hours)
                ).exists()
                
                # Only create notification if we haven't already notified about this item recently
                if not existing_notification:
                    Notification.objects.create(
                        user=manager,
                        message=notification_message,
                        activity_type="warning"
                    )
                    
    except Exception as e:
        # Fail silently to avoid breaking the dashboard
        print(f"Error creating consolidated low stock notifications: {e}")

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@user_passes_test(is_employee_or_manager)
def dashBoard(request):

    # Restrict direct URL access: only allow navigation via internal links
    referer = request.META.get('HTTP_REFERER', '')
    allowed_hosts = [request.get_host()]
    if referer:
        from urllib.parse import urlparse
        referer_host = urlparse(referer).netloc
        if referer_host not in allowed_hosts:
            return redirect('login')
    else:
        # No referer, likely direct access
        return redirect('login')

    user = request.user
    is_manager = user.groups.filter(name="Manager").exists()
    is_employee = user.groups.filter(name="Employee").exists()

    # Calculate statistics with consolidated stock data
    total_sales = Sale.objects.count()
    
    # Consolidate stock by product combination (sum quantities for same product)
    from django.db.models import Sum
    consolidated_stock = Stock.objects.values('product_name', 'product_type').annotate(
        total_quantity=Sum('quantity'),
        latest_date=models.Max('date')
    )
    
    # Calculate totals from consolidated data
    total_stock_items = sum(item['total_quantity'] for item in consolidated_stock)
    
    # Get out of stock products (consolidated quantity = 0)
    out_of_stock_products = [item for item in consolidated_stock if item['total_quantity'] == 0]
    out_of_stock_count = len(out_of_stock_products)
    
    # Convert to objects for template compatibility
    out_of_stock_items = []
    for item in out_of_stock_products:
        # Create a mock object with the required fields
        class MockStock:
            def __init__(self, product_name, product_type, date):
                self.product_name = product_name
                self.product_type = product_type
                self.date = date
        
        out_of_stock_items.append(MockStock(
            item['product_name'], 
            item['product_type'], 
            item['latest_date']
        ))
    
    # Get low stock products (consolidated quantity > 0 but < 5)
    low_stock_products = [item for item in consolidated_stock if 0 < item['total_quantity'] < 5]
    low_stock_count = len(low_stock_products)
    
    # Convert to objects for template compatibility
    low_stock_items = []
    for item in low_stock_products:
        class MockStock:
            def __init__(self, product_name, product_type, quantity):
                self.product_name = product_name
                self.product_type = product_type
                self.quantity = quantity
        
        low_stock_items.append(MockStock(
            item['product_name'], 
            item['product_type'], 
            item['total_quantity']
        ))
    
    # Get available products for sales form (consolidated quantity > 0)
    available_products = [item for item in consolidated_stock if item['total_quantity'] > 0]
    
    # Create automatic low stock notifications for managers (with consolidated data)
    create_low_stock_notifications_consolidated(low_stock_products)
    
    # Calculate total revenue from sales (using price field which is unit price)
    total_revenue = 0
    total_cost_of_sales = 0
    profit = 0
    for sale in Sale.objects.select_related('customer').all():
        try:
            # IMPROVED: Use foreign key relationship for better performance
            if sale.product_ref:
                stock_item = Stock.objects.filter(product_ref=sale.product_ref).first()
            else:
                # FALLBACK: Legacy string matching during migration period
                stock_item = Stock.objects.filter(product_name__iexact=sale.product_name, product_type__iexact=sale.product_type).first()
            
            # Use the unit_price and total_sales_amount from the Sale model itself
            if sale.unit_price and sale.total_sales_amount:
                sale_amount = float(sale.total_sales_amount)
            else:
                # Fallback calculation if total_sales_amount is not available
                if sale.unit_price and sale.quantity:
                    sale_amount = float(sale.unit_price) * sale.quantity
                    # Add 5% transport fee if transport is required
                    if sale.transport_required:
                        transport_fee = sale_amount * 0.05  # 5% transport fee
                        sale_amount += transport_fee
                else:
                    sale_amount = 0
                
            total_revenue += sale_amount
            
            # Calculate cost of sales for profit calculation
            # Try to get the actual cost of this product from stock records
            if sale.product_ref:
                stock_cost_items = Stock.objects.filter(product_ref=sale.product_ref)
            else:
                stock_cost_items = Stock.objects.filter(product_name__iexact=sale.product_name, product_type__iexact=sale.product_type)
            
            # Calculate average unit cost from new model fields
            unit_costs = []
            for stock_cost_item in stock_cost_items:
                if stock_cost_item.unit_cost and stock_cost_item.unit_cost > 0:
                    unit_costs.append(float(stock_cost_item.unit_cost))
            
            if unit_costs:
                    avg_unit_cost = sum(unit_costs) / len(unit_costs)
                    sale_cost = avg_unit_cost * sale.quantity
                    total_cost_of_sales += sale_cost
                    
        except (ValueError, TypeError):
            # Handle cases where price can't be converted to float
            continue
    
    # Calculate profit (Revenue - Cost of Sales)
    profit = total_revenue - total_cost_of_sales

    # Enrich sales data with amount calculations including transport fees
    sales_with_amounts = []
    for sale in Sale.objects.select_related('customer').all().order_by('-date'):
        try:
            # IMPROVED: Use foreign key relationship (much faster and more reliable)
            if sale.product_ref:
                # Use foreign key relationship - direct and efficient
                stock_item = Stock.objects.filter(product_ref=sale.product_ref).first()
            else:
                # FALLBACK: For legacy records without foreign key (during migration period)
                stock_item = Stock.objects.filter(product_name__iexact=sale.product_name, product_type__iexact=sale.product_type).first()
            
            # Use the sale's own unit_price and total_sales_amount
            if sale.unit_price and sale.quantity:
                total_amount = float(sale.total_sales_amount) if sale.total_sales_amount else float(sale.unit_price) * sale.quantity
                
                # Calculate transport fee (5% if transport required)
                transport_fee = 0
                if sale.transport_required:
                    base_amount = float(sale.unit_price) * sale.quantity
                    transport_fee = base_amount * 0.05
                    total_amount = base_amount + transport_fee
            else:
                total_amount = 0
                transport_fee = 0
                
        except (ValueError, TypeError):
            total_amount = 0
            transport_fee = 0
        
        # Create a copy of the sale with additional amount and transport fee info
        sale.total_amount = total_amount
        sale.transport_fee = transport_fee
        sales_with_amounts.append(sale)

    if is_manager:
        data = {
            "stock": Stock.objects.select_related('supplier').all(),
            "sales": sales_with_amounts,
            "employees": User.objects.filter(groups__name="Employee"),
            "total_sales": total_sales,
            "total_stock_items": total_stock_items,
            "out_of_stock_count": out_of_stock_count,
            "out_of_stock_items": out_of_stock_items,
            "low_stock_items": low_stock_items,
            "low_stock_count": low_stock_count,
            "available_products": available_products,
            "total_revenue": total_revenue,
            "total_cost_of_sales": total_cost_of_sales,
            "profit": profit,
        }
    elif is_employee:
        data = {
            "stock": Stock.objects.select_related('supplier').all(),
            "sales": sales_with_amounts,
            "total_sales": total_sales,
            "total_stock_items": total_stock_items,
            "out_of_stock_count": out_of_stock_count,
            "out_of_stock_items": out_of_stock_items,
            "low_stock_items": low_stock_items,
            "low_stock_count": low_stock_count,
            "available_products": available_products,
            "total_revenue": total_revenue,
            "total_cost_of_sales": total_cost_of_sales,
            "profit": profit,
        }
    else:
        data = {}

    return render(request, "dashboard.html", {
        "data": data,
        "is_manager": is_manager,
        "is_employee": is_employee,
    })



@login_required
@user_passes_test(is_employee_or_manager)
def activityFeed(request):
    # If user is a manager, show all notifications for all managers
    if request.user.groups.filter(name="Manager").exists():
        manager_ids = User.objects.filter(groups__name="Manager").values_list('id', flat=True)
        activities = Notification.objects.filter(user_id__in=manager_ids).order_by('-created_at')[:10]
    else:
        activities = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    data = [
        {
            "id": a.id,
            "message": a.message,
            "time": a.created_at.strftime("%b %d, %Y %H:%M"),
            "type": a.activity_type,
            "is_read": a.is_read
        }
        for a in activities
    ]
    return JsonResponse({"activities": data})


# Mark notification as read
@csrf_exempt
@require_POST
@login_required
@user_passes_test(is_employee_or_manager)
def mark_notification_read(request):
    import json
    data = json.loads(request.body)
    notif_id = data.get('id')
    try:
        notif = Notification.objects.get(id=notif_id)
        notif.is_read = True
        notif.save()
        return JsonResponse({"success": True})
    except Notification.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"}, status=404)

@login_required
@user_passes_test(is_employee_or_manager)
@csrf_exempt
def mark_all_notifications_read(request):
    if request.method == "POST":
        # Mark all unread notifications for the current user as read
        updated_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        
        return JsonResponse({"success": True, "updated_count": updated_count})
    
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

@login_required
@user_passes_test(is_employee_or_manager)
def notifications(request):
    # Get only unread notifications for the modal
    unread_notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).order_by('-created_at')[:20]  # Limit to recent 20 notifications
    
    unread_count = unread_notifications.count()
    
    data = [
        {
            "id": n.id,
            "message": n.message, 
            "time": n.created_at.isoformat(),  # Use ISO format for better JavaScript parsing
            "activity_type": n.activity_type,
            "is_read": n.is_read
        }
        for n in unread_notifications
    ]
    return JsonResponse({"notifications": data, "count": unread_count})

@login_required
@user_passes_test(is_employee_or_manager)
def stock_data_api(request):
    """
    API endpoint to provide stock data as JSON for JavaScript consumption
    Clean separation between Django backend and frontend JavaScript
    """
    try:
        from django.db.models import Sum
        
        # Get consolidated stock data
        available_products = Stock.objects.values('product_name', 'product_type').annotate(
            quantity=Sum('quantity')
        ).filter(quantity__gt=0)
        
        # Convert to JavaScript-friendly format
        stock_data = {}
        for product in available_products:
            key = f"{product['product_name']}-{product['product_type']}"
            stock_data[key] = product['quantity']
        
        return JsonResponse({
            "success": True,
            "stock_data": stock_data,
            "total_products": len(stock_data),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
            "stock_data": {}
        }, status=500)


@login_required
@manager_required
def employee_list(request):
    # Get all users who are in Employee or Manager groups
    employees = User.objects.filter(groups__name__in=['Employee', 'Manager']).distinct()
    return render(request, "employee_list.html", {"Employee": employees})









@login_required
@user_passes_test(is_employee_or_manager)
@manager_required
def report(request):
    if request.method == "POST":
        report_type = request.POST.get("report_type")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        if report_type == "sales":
            return redirect(f"/sales_report/?start_date={start_date}&end_date={end_date}")
        elif report_type == "stock":
            return redirect('stock_report')
        else:
            return render(request, 'gen_report.html', {'error': 'Invalid selection'})
    return render(request, 'gen_report.html')

@secure_view
@login_required
@user_passes_test(is_employee_or_manager)
@manager_required
def sales_report(request):
    """
    Sales Report View (Reports Section) - Enhanced with data filtering
    Shows all sales with date filtering and manager information
    """
    from django.contrib.auth.models import User
    from datetime import date
    
    # Get filter parameters
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    
    # Get all sales, apply date filters if provided
    all_sales = Sale.objects.select_related('customer').all().order_by('-date')
    
    if start_date:
        all_sales = all_sales.filter(date__gte=start_date)
    if end_date:
        all_sales = all_sales.filter(date__lte=end_date)
    
    # Get current user's manager info or first available manager
    current_manager = request.user
    if not current_manager.groups.filter(name='Manager').exists():
        # If current user is not manager, get first available manager
        managers = User.objects.filter(groups__name='Manager').first()
        current_manager = managers if managers else request.user
    
    context = {
        'sales': all_sales,
        'start_date': start_date,
        'end_date': end_date,
        'manager_name': current_manager.get_full_name() or current_manager.username,
        'report_date': date.today(),
        'total_sales': all_sales.count(),
        'is_filtered': bool(start_date or end_date)
    }
    
    return render(request, 'sales_report.html', context)

@login_required
@user_passes_test(is_employee_or_manager)
@manager_required
def stock_report(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    
    # Get all stock records
    all_Stock = Stock.objects.select_related('supplier').all()
    
    # Get manager name (same as sales report)
    manager_name = f"{request.user.first_name} {request.user.last_name}".strip()
    if not manager_name:
        manager_name = request.user.username
    
    # Get current date for report generation
    from datetime import date
    report_date = date.today()
    
    return render(request, 'stock_report.html', {
        'start_date': start_date,
        'end_date': end_date,
        'stocks': all_Stock,
        'manager_name': manager_name,
        'report_date': report_date,
    })

@secure_view
@login_required
@user_passes_test(is_employee_or_manager)
def saleRecord(request):
    all_Sales = Sale.objects.select_related('customer').all()
    context = {
        "Sales" : all_Sales
    }
    return render(request, 'sales.html', context)

@login_required
@user_passes_test(is_employee_or_manager)
def generateReceipt(request, product_id):
    """
    Generate Receipt View - Creates printable receipt for a sale
    Includes sale details, transport fees, and company information
    """
    sale = get_object_or_404(Sale, id=product_id)
    
    # Calculate sale details including transport fee
    try:
        # IMPROVED: Use foreign key relationship for better performance and reliability
        if sale.product_ref:
            stock_item = Stock.objects.filter(product_ref=sale.product_ref).first()
        else:
            # FALLBACK: Legacy string matching during migration period
            stock_item = Stock.objects.filter(product_name__iexact=sale.product_name, product_type__iexact=sale.product_type).first()
        
        if stock_item:
            unit_price = float(stock_item.price) if stock_item.price else 0
            subtotal = unit_price * sale.quantity
            
            # Calculate transport fee (5% if required)
            transport_fee = 0
            if sale.transport_required:
                transport_fee = subtotal * 0.05
            
            total_amount = subtotal + transport_fee
        else:
            unit_price = 0
            subtotal = 0
            transport_fee = 0
            total_amount = 0
        
    except (ValueError, TypeError):
        unit_price = 0
        subtotal = 0
        transport_fee = 0
        total_amount = 0
    
    context = {
        'sale': sale,
        'unit_price': unit_price,
        'subtotal': subtotal,
        'transport_fee': transport_fee,
        'total_amount': total_amount,
        'receipt_number': f"MWF-{sale.id:06d}",  # Format: MWF-000001
        'company_name': 'Mayondo Wood & Furniture Ltd',
        'company_address': 'Furniture Showroom & Warehouse',
        'company_phone': '+256 772 402 070',
    }
    
    return render(request, 'receipt.html', context)

@secure_view
@login_required
@user_passes_test(is_employee_or_manager)
def addSale(request):
    """
    Add Sale View - Creates new sales records with stock validation
    Validates that sufficient stock exists before allowing the sale
    Includes transport fee calculation (5% when transport required)
    """
    if request.method == 'POST':
        form = SaleForm(request.POST)
        print(f"DEBUG: Form POST data: {request.POST}")
        if form.is_valid():
            # Get form data before saving
            product_name = form.cleaned_data['product_name']
            product_type = form.cleaned_data['product_type']
            quantity_to_sell = form.cleaned_data['quantity']
            print(f"DEBUG: Form is valid. Product: {product_name} ({product_type}), Quantity: {quantity_to_sell}")

            # ✅ Check consolidated stock for this product combination
            from django.db.models import Sum
            consolidated_stock = Stock.objects.filter(
                product_name=product_name, 
                product_type=product_type
            ).aggregate(total_quantity=Sum('quantity'))
            
            total_available = consolidated_stock['total_quantity'] or 0
            
            # Find a stock record with available quantity to deduct from
            stock_item = Stock.objects.filter(
                product_name=product_name, 
                product_type=product_type,
                quantity__gt=0
            ).first()

            if total_available <= 0 or not stock_item:
                # Check if there are any similar products available
                available_products = Stock.objects.filter(
                    product_name=product_name, 
                    quantity__gt=0
                ).values_list('product_type', flat=True).distinct()
                
                error_msg = f"❌ Cannot record sale: {product_name} ({product_type}) is not available in stock! "
                
                if available_products:
                    available_types = ", ".join(available_products)
                    error_msg += f"However, {product_name} is available in these types: {available_types}. "
                    error_msg += "Please select the correct product type."
                else:
                    error_msg += f"This product '{product_name}' is not in inventory at all. "
                    error_msg += "Contact your manager for assistance."
                
                print(f"DEBUG: {error_msg}")
                messages.error(request, error_msg)
                available_products = Stock.objects.values('product_name', 'product_type').annotate(
                    quantity=Sum('quantity')
                ).filter(quantity__gt=0)
                return render(request, 'add_sale.html', {
                    'form': form,
                    'data': {'available_products': available_products}
                })

            # ✅ Check if enough consolidated stock is available
            if total_available < quantity_to_sell:
                messages.error(
                    request,
                    f'❌ Insufficient stock for {product_name} ({product_type})! '
                    f'Available quantity: {total_available} units, Requested: {quantity_to_sell} units. '
                    f'Please reduce the quantity to proceed with the sale.'
                )
                available_products = Stock.objects.values('product_name', 'product_type').annotate(
                    quantity=Sum('quantity')
                ).filter(quantity__gt=0)
                return render(request, 'add_sale.html', {
                    'form': form,
                    'data': {'available_products': available_products}
                })

            # ✅ Check if consolidated stock quantity would go to zero
            if total_available == quantity_to_sell:
                messages.warning(
                    request,
                    f'⚠️ Note: This sale has completely exhausted the stock for {product_name} ({product_type}). '
                    f'Consider restocking this item soon.'
                )

            # Stock is sufficient - create the sale
            new_sale = form.save()

            # Update stock quantity (may need to deduct from multiple records)
            remaining_to_deduct = quantity_to_sell
            stock_records = Stock.objects.filter(
                product_name=product_name, 
                product_type=product_type,
                quantity__gt=0
            ).order_by('-date')  # Deduct from newest stock first
            
            for record in stock_records:
                if remaining_to_deduct <= 0:
                    break
                
                if record.quantity >= remaining_to_deduct:
                    # This record has enough stock
                    record.quantity -= remaining_to_deduct
                    record.save()
                    remaining_to_deduct = 0
                else:
                    # Partially use this record and continue to next
                    remaining_to_deduct -= record.quantity
                    record.quantity = 0
                    record.save()

            # Transport fee info
            transport_fee_message = ""
            if new_sale.transport_required:
                transport_fee_message = " (5% transport fee included)"

            # Notify managers
            managers = User.objects.filter(groups__name="Manager")
            for manager in managers:
                Notification.objects.create(
                    user=manager,
                    message=f"New sale recorded: {product_name} ({product_type}) - {new_sale.quantity} units "
                            f"by {new_sale.sales_agent}{transport_fee_message}",
                    activity_type="success"
                )

            # Calculate remaining stock after deduction
            remaining_stock = Stock.objects.filter(
                product_name=product_name, 
                product_type=product_type
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            messages.success(
                request,
                f'Sale recorded successfully! Stock updated: {remaining_stock} remaining{transport_fee_message}'
            )
            return redirect('saleRecord')
        else:
            print(f"DEBUG: Form is NOT valid. Errors: {form.errors}")
            messages.error(request, f"Please correct the following errors: {form.errors}")
    else:
        form = SaleForm()
    
    # Get available products for JavaScript stock validation (consolidated)
    from django.db.models import Sum
    available_products = Stock.objects.values('product_name', 'product_type').annotate(
        quantity=Sum('quantity')
    ).filter(quantity__gt=0)

    return render(request, 'add_sale.html', {
        'form': form,
        'data': {'available_products': available_products}
    })



@login_required
@user_passes_test(is_employee_or_manager)
def editSale(request, product_id):
    sale_to_edit = get_object_or_404(Sale, id=product_id)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sale updated successfully!')
            return redirect('/saleRecord/')
    else:
        form = SaleForm(instance=sale_to_edit)
    
    context = {
        "selected": sale_to_edit,
        "form": form
    }
    
    return render(request, 'edit_sale.html', context)

@login_required
@user_passes_test(is_employee_or_manager)
def viewSingleSale(request, product_id):
    
    #IMPROVED: View sale details 
    
    sale = get_object_or_404(Sale, id=product_id)
    context = {'sale': sale}  
    return render(request, 'view_sale.html', context)

@login_required
@user_passes_test(is_employee_or_manager)
def updateSale(request, product_id):
    sale_to_update = get_object_or_404(Sale, id=product_id)
    if request.method == 'POST':
        form_data = request.POST
        new_product_type = form_data.get('product_type')
        sale_to_update.product_type = new_product_type
        sale_to_update.save()
        return redirect('/saleRecord/')
    context = {
        "selected": sale_to_update
    }
    return render(request, 'update_sale.html', context)


@login_required
@user_passes_test(is_employee_or_manager)
def deleteSale(request, product_id):
    sale_to_delete = get_object_or_404(Sale, id=product_id)
    if request.method == 'POST':
        sale_to_delete.delete()
        return redirect('/saleRecord/')
    # If GET request, show confirmation page
    context = {
        'selected': sale_to_delete
    }
    return render(request, 'confirm_delete.html', context)





@secure_view
@login_required
@user_passes_test(is_employee_or_manager)
@manager_required
def saleReport(request):
    """
    Sales Report View (Sales Section) - Enhanced to match reports section
    Shows all sales with manager information and generation date
    """
    from django.contrib.auth.models import User
    from datetime import date
    
    # Get filter parameters (if any)
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    
    # Get all sales, apply date filters if provided
    all_sales = Sale.objects.select_related('customer').all().order_by('-date')
    
    if start_date:
        all_sales = all_sales.filter(date__gte=start_date)
    if end_date:
        all_sales = all_sales.filter(date__lte=end_date)
    
    # Get current user's manager info or first available manager
    current_manager = request.user
    if not current_manager.groups.filter(name='Manager').exists():
        # If current user is not manager, get first available manager
        managers = User.objects.filter(groups__name='Manager').first()
        current_manager = managers if managers else request.user
    
    context = {
        'sales': all_sales,
        'start_date': start_date,
        'end_date': end_date,
        'manager_name': current_manager.get_full_name() or current_manager.username,
        'report_date': date.today(),
        'total_sales': all_sales.count(),
        'is_filtered': bool(start_date or end_date)
    }
    
    return render(request, "sales_report.html", context)

@login_required
@user_passes_test(is_employee_or_manager)
def stockRecord(request):
    all_Stocks = Stock.objects.select_related('supplier').all()
    context = {
        "Stocks" : all_Stocks
    }
    return render(request, 'stock.html', context)

@login_required
@user_passes_test(is_employee_or_manager)
def addStock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            new_stock = form.save()
            # Notify all managers
            managers = User.objects.filter(groups__name="Manager")
            for manager in managers:
                Notification.objects.create(
                    user=manager,
                    message=f"New stock added: {new_stock.product_name} ({new_stock.quantity}) from {new_stock.supplier_name}",
                    activity_type="info"
                )
            messages.success(request, 'Stock added successfully!')
            return redirect('/stockRecord/')
    else:
        form = StockForm()
    
    return render(request, 'add_stock.html', {'form': form})

@login_required
@user_passes_test(is_employee_or_manager)
def editStock(request, product_id):
    stock_to_edit = get_object_or_404(Stock, id=product_id)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock updated successfully!')
            return redirect('/stockRecord/')
    else:
        form = StockForm(instance=stock_to_edit)
    
    context = {
        "selected": stock_to_edit,
        "form": form
    }
    
    return render(request, 'edit_stock.html', context)

@login_required
@user_passes_test(is_employee_or_manager)
def viewSingleStock(request, product_id):
    """
    IMPROVED: View stock details without unnecessary form overhead
    Just display the data cleanly - no form needed for view-only content
    """
    stock = get_object_or_404(Stock, id=product_id)
    context = {'stock': stock}  # Simple and clean - no form needed!
    return render(request, 'view_stock.html', context)

@login_required
@user_passes_test(is_employee_or_manager)
def deleteStock(request, product_id):
    stock_to_delete = get_object_or_404(Stock, id=product_id)
    if request.method == 'POST':
        stock_to_delete.delete()
        return redirect('/stockRecord/')
    # If GET request, show confirmation page
    context = {
        'selected': stock_to_delete
    }
    return render(request, 'confirm_delete_stock.html', context)
    

@login_required
@user_passes_test(is_employee_or_manager)
def updateStock(request, product_id):
    stock_to_update = get_object_or_404(Stock, id=product_id)
    if request.method == 'POST':
        form_data = request.POST
        new_product_type = form_data.get('product_type')
        stock_to_update.product_type = new_product_type
        stock_to_update.save()
        return redirect('/stockRecord/')
    context = {
        "selected": stock_to_update
    }
    return render(request, 'update_stock.html', context)

@manager_required
def stockReport(request):
    all_Stock = Stock.objects.select_related('supplier').all()
    
    # Get manager name (same as sales report)
    manager_name = f"{request.user.first_name} {request.user.last_name}".strip()
    if not manager_name:
        manager_name = request.user.username
    
    # Get current date for report generation
    from datetime import date
    report_date = date.today()

    context = {
        "stocks": all_Stock,
        "manager_name": manager_name,
        "report_date": report_date,
    }
    return render(request, "stock_report.html", context)


# ===== CUSTOMER MANAGEMENT VIEWS =====

def customerList(request):
    """Display list of all customers - accessible by both managers and employees"""
    customers = Customer.objects.all().order_by('-created_at')
    
    context = {
        'customers': customers,
        'is_manager': request.user.groups.filter(name="Manager").exists(),
        'is_employee': request.user.groups.filter(name="Employee").exists(),
    }
    return render(request, 'customerlist.html', context)


def addCustomer(request):
    """Add new customer - accessible by both managers and employees"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            
            # Create notification for all managers
            try:
                managers = User.objects.filter(groups__name="Manager")
                for manager in managers:
                    Notification.objects.create(
                        user=manager,
                        message=f"🆕 NEW CUSTOMER: {customer.name} has been added by {request.user.get_full_name() or request.user.username}",
                        activity_type="success"
                    )
            except Exception as e:
                # Fail silently to avoid breaking the customer creation
                print(f"Error creating customer notification: {e}")
            
            messages.success(request, f'Customer "{customer.name}" added successfully!')
            return redirect('customerList')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'is_manager': request.user.groups.filter(name="Manager").exists(),
        'is_employee': request.user.groups.filter(name="Employee").exists(),
    }
    return render(request, 'add_customer.html', context)


def editCustomer(request, customer_id):
    """Edit existing customer - accessible by both managers and employees"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.name}" updated successfully!')
            return redirect('customerList')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'form': form,
        'customer': customer,
        'is_manager': request.user.groups.filter(name="Manager").exists(),
        'is_employee': request.user.groups.filter(name="Employee").exists(),
    }
    return render(request, 'edit_customer.html', context)


def deleteCustomer(request, customer_id):
    """Delete customer - accessible by both managers and employees"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        customer_name = customer.name
        customer.delete()
        messages.success(request, f'Customer "{customer_name}" deleted successfully!')
        return redirect('customerList')
    
    context = {
        'customer': customer,
        'is_manager': request.user.groups.filter(name="Manager").exists(),
        'is_employee': request.user.groups.filter(name="Employee").exists(),
    }
    return render(request, 'delete_customer.html', context)


# ===== SUPPLIER MANAGEMENT VIEWS =====

def supplierList(request):
    """Display list of all suppliers - accessible by both managers and employees"""
    suppliers = Supplier.objects.all().order_by('-created_at')
    
    context = {
        'suppliers': suppliers,
        'is_manager': request.user.groups.filter(name="Manager").exists(),
        'is_employee': request.user.groups.filter(name="Employee").exists(),
    }
    return render(request, 'supplierlist.html', context)


def addSupplier(request):
    """Add new supplier - accessible by both managers and employees"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            
            # Create notification for all managers
            try:
                managers = User.objects.filter(groups__name="Manager")
                for manager in managers:
                    Notification.objects.create(
                        user=manager,
                        message=f"🆕 NEW SUPPLIER: {supplier.name} has been added by {request.user.get_full_name() or request.user.username}",
                        activity_type="success"
                    )
            except Exception as e:
                # Fail silently to avoid breaking the supplier creation
                print(f"Error creating supplier notification: {e}")
            
            messages.success(request, f'Supplier "{supplier.name}" added successfully!')
            return redirect('supplierList')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SupplierForm()
    
    context = {
        'form': form,
        'is_manager': request.user.groups.filter(name="Manager").exists(),
        'is_employee': request.user.groups.filter(name="Employee").exists(),
    }
    return render(request, 'add_supplier.html', context)


def editSupplier(request, supplier_id):
    """Edit existing supplier - accessible by both managers and employees"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.name}" updated successfully!')
            return redirect('supplierList')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SupplierForm(instance=supplier)
    
    context = {
        'form': form,
        'supplier': supplier,
        'is_manager': request.user.groups.filter(name="Manager").exists(),
        'is_employee': request.user.groups.filter(name="Employee").exists(),
    }
    return render(request, 'edit_supplier.html', context)


def deleteSupplier(request, supplier_id):
    """Delete supplier - accessible by both managers and employees"""
    supplier = get_object_or_404(Supplier, id=supplier_id)
    
    if request.method == 'POST':
        supplier_name = supplier.name
        supplier.delete()
        messages.success(request, f'Supplier "{supplier_name}" deleted successfully!')
        return redirect('supplierList')
    
    context = {
        'supplier': supplier,
        'is_manager': request.user.groups.filter(name="Manager").exists(),
        'is_employee': request.user.groups.filter(name="Employee").exists(),
    }
    return render(request, 'delete_supplier.html', context)


# ===== EMPLOYEE MANAGEMENT VIEWS =====

@manager_required
def addEmployee(request):
    """Add new employee - accessible by managers only"""
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )
            
            # Add to Employee group
            from django.contrib.auth.models import Group
            employee_group, created = Group.objects.get_or_create(name='Employee')
            user.groups.add(employee_group)
            
            # Create notification for all managers (including the current one who added the employee)
            try:
                managers = User.objects.filter(groups__name="Manager")
                for manager in managers:
                    Notification.objects.create(
                        user=manager,
                        message=f"👤 NEW EMPLOYEE: {first_name} {last_name} ({username}) has been added by {request.user.get_full_name() or request.user.username}",
                        activity_type="success"
                    )
            except Exception as e:
                # Fail silently to avoid breaking the employee creation
                print(f"Error creating employee notification: {e}")
            
            messages.success(request, f'Employee "{first_name} {last_name}" added successfully!')
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Error creating employee: {str(e)}')
    
    context = {
        'is_manager': True,
        'is_employee': False,
    }
    return render(request, 'add_employee.html', context)


@manager_required
def editEmployee(request, employee_id):
    """Edit existing employee - accessible by managers only"""
    employee = get_object_or_404(User, id=employee_id)
    
    if request.method == 'POST':
        employee.first_name = request.POST.get('first_name', '')
        employee.last_name = request.POST.get('last_name', '')
        employee.email = request.POST.get('email', '')
        
        # Update password if provided
        new_password = request.POST.get('password')
        if new_password:
            employee.set_password(new_password)
        
        employee.save()
        messages.success(request, f'Employee "{employee.first_name} {employee.last_name}" updated successfully!')
        return redirect('employee_list')
    
    context = {
        'employee': employee,
        'is_manager': True,
        'is_employee': False,
    }
    return render(request, 'edit_employee.html', context)


@manager_required
def deleteEmployee(request, employee_id):
    """Delete employee - accessible by managers only"""
    employee = get_object_or_404(User, id=employee_id)
    
    if request.method == 'POST':
        employee_name = f"{employee.first_name} {employee.last_name}".strip() or employee.username
        employee.delete()
        messages.success(request, f'Employee "{employee_name}" deleted successfully!')
        return redirect('employee_list')
    
    context = {
        'employee': employee,
        'is_manager': True,
        'is_employee': False,
    }
    return render(request, 'delete_employee.html', context)

@login_required
@user_passes_test(is_employee_or_manager)
def viewCustomer(request, customer_id):
    """
    View customer details - display customer information in a clean format
    """
    customer = get_object_or_404(Customer, id=customer_id)
    context = {'customer': customer}
    return render(request, 'view_customer.html', context)

@login_required
@user_passes_test(is_employee_or_manager)
def viewSupplier(request, supplier_id):
    """
    View supplier details - display supplier information in a clean format
    """
    supplier = get_object_or_404(Supplier, id=supplier_id)
    context = {'supplier': supplier}
    return render(request, 'view_supplier.html', context)


