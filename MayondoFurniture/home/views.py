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
    Login Page View - Handles user authentication
    Supports role-based login (Manager/Employee) with group verification
    Redirects to dashboard on successful login, shows error messages on failure
    """
    if request.method == "POST":
        # Get login credentials from form
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")  # Manager or Employee role selection

        # Validate required fields
        if not username or not password or not role:
            messages.error(request, "Please fill in all required fields.")
            return render(request, "login.html")

        # Attempt to authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if user account is active
            if not user.is_active:
                messages.error(request, "Your account has been deactivated. Please contact an administrator.")
                return render(request, "login.html")
            
            # Verify user belongs to the selected role group
            if user.groups.filter(name=role).exists():
                login(request, user)  # Start user session
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                return redirect("dashboard")  # Successful login - go to dashboard
            else:
                messages.error(request, f"Access denied. You are not authorized for the '{role}' role. Please check your role selection or contact an administrator.")
                return render(request, "login.html")
        else:
            # Check if username exists to provide more specific error
            from django.contrib.auth.models import User
            try:
                existing_user = User.objects.get(username=username)
                messages.error(request, "Incorrect password. Please try again or contact an administrator if you've forgotten your password.")
            except User.DoesNotExist:
                messages.error(request, "Username not found. Please check your username or contact an administrator for account registration.")
            
            return render(request, "login.html")

    # GET request - display login form
    return render(request, "login.html")


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
    messages.success(request, 'You have been logged out successfully. For security, please close your browser.')
    
    # Create response with strict cache control headers
    response = render(request, "logout.html")
    
    # Prevent caching of any authenticated pages
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response



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
def employee_list(request):
    # Get all users who are in Employee or Manager groups
    employees = User.objects.filter(groups__name__in=['Employee', 'Manager']).distinct()
    return render(request, "employee_list.html", {"Employee": employees})



@login_required
@user_passes_test(is_employee_or_manager)
def addEmployee(request):
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        title = request.POST["title"]

        try:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' is already taken. Please choose a different username.")
                return render(request, "add_employee.html")
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, f"Email '{email}' is already registered. Please use a different email.")
                return render(request, "add_employee.html")

            # Create User
            new_user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            # Add user to appropriate group based on title
            from django.contrib.auth.models import Group
            if title in ["SalesAgent", "StockClerk"]:
                group_name = "Employee"
            else:
                group_name = "Manager"
            
            group, created = Group.objects.get_or_create(name=group_name)
            new_user.groups.add(group)

            # Notify managers
            managers = User.objects.filter(groups__name="Manager")
            for manager in managers:
                Notification.objects.create(
                    user=manager,
                    message=f"A new {group_name.lower()} '{new_user.username}' was added with role: {title}.",
                    activity_type="info"
                )

            messages.success(request, f"Employee '{username}' has been successfully created with role: {title}.")
            return redirect("employee_list")
            
        except Exception as e:
            messages.error(request, f"An error occurred while creating the employee: {str(e)}")
            return render(request, "add_employee.html")

    return render(request, "add_employee.html")





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
    all_sales = Sale.objects.all().order_by('-date')
    
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
    all_Stock = Stock.objects.all()
    
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

            # ✅ Find the stock record for this product combination
            stock_item = Stock.objects.filter(
                product_name=product_name, 
                product_type=product_type
            ).first()

            if not stock_item:
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
                return render(request, 'add_sale.html', {'form': form})

            # ✅ Check if enough stock is available
            if stock_item.quantity < quantity_to_sell:
                messages.error(
                    request,
                    f'❌ Insufficient stock for {product_name} ({product_type})! '
                    f'Available quantity: {stock_item.quantity} units, Requested: {quantity_to_sell} units. '
                    f'Please reduce the quantity to proceed with the sale.'
                )
                return render(request, 'add_sale.html', {'form': form})

            # ✅ Check if stock quantity would go to zero or negative
            if stock_item.quantity == quantity_to_sell:
                messages.warning(
                    request,
                    f'⚠️ Note: This sale will completely exhaust the stock for {product_name} ({product_type}). '
                    f'Consider restocking this item soon.'
                )

            # Stock is sufficient - create the sale
            new_sale = form.save()

            # Update stock quantity
            stock_item.quantity -= quantity_to_sell
            stock_item.save()

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

            messages.success(
                request,
                f'Sale recorded successfully! Stock updated: {stock_item.quantity} remaining{transport_fee_message}'
            )
            return redirect('saleRecord')
        else:
            print(f"DEBUG: Form is NOT valid. Errors: {form.errors}")
            messages.error(request, f"Please correct the following errors: {form.errors}")
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
    all_sales = Sale.objects.all().order_by('-date')
    
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




