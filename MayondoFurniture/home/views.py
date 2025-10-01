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
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse
from functools import wraps

# Local application imports
from home.models import Sale, Stock, Notification
from .forms import SaleForm, StockForm

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
    Login Page View - Handles user authentication
    Supports role-based login (Manager/Employee) with group verification
    Redirects to dashboard on successful login, shows error messages on failure
    """
    if request.method == "POST":
        # Get login credentials from form
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")  # Manager or Employee role selection

        # Attempt to authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Verify user belongs to the selected role group
            if user.groups.filter(name=role).exists():
                login(request, user)  # Start user session
                return redirect("dashboard")  # Successful login - go to dashboard
            else:
                messages.error(request, "You are not authorized as this role.")
                return redirect("login")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    # GET request - display login form
    return render(request, "login.html")


def logoutPage(request):
    """
    Logout Page View - Handles user logout
    Terminates user session and displays logout confirmation page
    """
    # Terminate user session
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return render(request, "logout.html")



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

    # Calculate statistics
    total_sales = Sale.objects.count()
    total_stock_items = Stock.objects.aggregate(total=models.Sum('quantity'))['total'] or 0
    out_of_stock_count = Stock.objects.filter(quantity=0).count()
    
    # Calculate total revenue from sales (using price field which is unit price)
    total_revenue = 0
    for sale in Sale.objects.all():
        try:
            # IMPROVED: Use foreign key relationship for better performance
            if sale.product_ref:
                stock_item = Stock.objects.filter(product_ref=sale.product_ref).first()
            else:
                # FALLBACK: Legacy string matching during migration period
                stock_item = Stock.objects.filter(product_name__iexact=sale.product_name, product_type__iexact=sale.product_type).first()
            
            if stock_item:
                # Convert price from CharField to float and multiply by quantity
                unit_price = float(stock_item.price) if stock_item.price else 0
                sale_amount = unit_price * sale.quantity
                
                # Add 5% transport fee if transport is required
                if sale.transport_required:
                    transport_fee = sale_amount * 0.05  # 5% transport fee
                    sale_amount += transport_fee
                
                total_revenue += sale_amount
        except (ValueError, TypeError):
            # Handle cases where price can't be converted to float
            continue

    # Enrich sales data with amount calculations including transport fees
    sales_with_amounts = []
    for sale in Sale.objects.all().order_by('-date'):
        try:
            # IMPROVED: Use foreign key relationship (much faster and more reliable)
            if sale.product_ref:
                # Use foreign key relationship - direct and efficient
                stock_item = Stock.objects.filter(product_ref=sale.product_ref).first()
            else:
                # FALLBACK: For legacy records without foreign key (during migration period)
                stock_item = Stock.objects.filter(product_name__iexact=sale.product_name, product_type__iexact=sale.product_type).first()
            
            if stock_item:
                unit_price = float(stock_item.price) if stock_item.price else 0
                total_amount = unit_price * sale.quantity
                
                # Calculate transport fee (5% if transport required)
                transport_fee = 0
                if sale.transport_required:
                    transport_fee = total_amount * 0.05
                    total_amount += transport_fee
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
            "stock": Stock.objects.all(),
            "sales": sales_with_amounts,
            "employees": User.objects.filter(groups__name="Employee"),
            "total_sales": total_sales,
            "total_stock_items": total_stock_items,
            "out_of_stock_count": out_of_stock_count,
            "total_revenue": total_revenue,
        }
    elif is_employee:
        data = {
            "stock": Stock.objects.all(),
            "sales": sales_with_amounts,
            "total_sales": total_sales,
            "total_stock_items": total_stock_items,
            "out_of_stock_count": out_of_stock_count,
            "total_revenue": total_revenue,
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
def addUser(request):
    if request.method == 'POST':
        # You may need to adjust this logic to match your user creation form
        username = request.POST.get('username')
        # ... other user fields ...
        # After creating the user:
        # new_user = User.objects.create_user(...)
        # Notify all managers
        managers = User.objects.filter(groups__name="Manager")
        for manager in managers:
            Notification.objects.create(
                user=manager,
                message=f"A new user was added to the system.",
                activity_type="info"
            )
    return render(request, "add_user.html")


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

@login_required
@user_passes_test(is_employee_or_manager)
@manager_required
def sales_report(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    return render(request, 'sales_report.html', {
        'start_date': start_date,
        'end_date': end_date
    })

@login_required
@user_passes_test(is_employee_or_manager)
@manager_required
def stock_report(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    return render(request, 'stock_report.html', {
        'start_date': start_date,
        'end_date': end_date
    })

@login_required
@user_passes_test(is_employee_or_manager)
def saleRecord(request):
    all_Sales = Sale.objects.all()
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
        if form.is_valid():
            # Get form data before saving
            product_name = form.cleaned_data['product_name']
            product_type = form.cleaned_data['product_type']
            quantity_to_sell = form.cleaned_data['quantity']
            
            # Validate stock availability before creating sale (case-insensitive match)
            try:
                # Use filter().first() to handle multiple stock items with same name/type
                stock_item = Stock.objects.filter(product_name__iexact=product_name, product_type__iexact=product_type).first()
                if not stock_item:
                    messages.error(request, f'Stock item not found for {product_name} - {product_type}!')
                    return render(request, 'add_sale.html', {'form': form})
                
                if stock_item.quantity < quantity_to_sell:
                    messages.error(request, f'Insufficient stock for {product_name} - {product_type}! Available: {stock_item.quantity}, Requested: {quantity_to_sell}')
                    return render(request, 'add_sale.html', {'form': form})
                
                # Stock is sufficient - create the sale (product_id will be auto-generated)
                new_sale = form.save()
                
                # Update stock quantity (reduce by sold amount)
                stock_item.quantity -= quantity_to_sell
                stock_item.save()
                
                # Calculate transport fee if applicable
                transport_fee_message = ""
                if new_sale.transport_required:
                    transport_fee_message = " (5% transport fee included)"
                
                # Notify all managers
                managers = User.objects.filter(groups__name="Manager")
                for manager in managers:
                    Notification.objects.create(
                        user=manager,
                        message=f"New sale recorded: {new_sale.product_name} ({new_sale.quantity}) by {new_sale.sales_agent}{transport_fee_message}",
                        activity_type="success"
                    )
                
                messages.success(request, f'Sale recorded successfully! Stock updated: {stock_item.quantity} remaining{transport_fee_message}')
                return redirect('/saleRecord/')
                
            except Stock.DoesNotExist:
                messages.error(request, f'{product_name} - {product_type} not found in stock. Please add to inventory first.')
                return render(request, 'add_sale.html', {'form': form})
                
    else:
        form = SaleForm()
    
    return render(request, 'add_sale.html', {'form': form})

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
    """
    IMPROVED: View sale details without unnecessary form overhead
    Just display the data cleanly - no form needed for view-only content
    """
    sale = get_object_or_404(Sale, id=product_id)
    context = {'sale': sale}  # Simple and clean - no form needed!
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





@login_required
@user_passes_test(is_employee_or_manager)
@manager_required
def saleReport(request):
    all_Sale = Sale.objects.all()

    context = {
        "sales": all_Sale
    }
    return render(request, "sales_report.html", context)

@login_required
@user_passes_test(is_employee_or_manager)
def stockRecord(request):
    all_Stocks = Stock.objects.all()
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
    all_Stock = Stock.objects.all()

    context = {
        "stocks": all_Stock
    }
    return render(request, "stock_report.html", context)




