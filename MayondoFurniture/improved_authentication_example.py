# IMPROVED AUTHENTICATION APPROACH
# Better than referer checking

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied

# ====== BETTER APPROACH 1: Use @login_required ======
@login_required  # Built-in Django decorator - much more reliable!
def viewSingleSale(request, product_id):
    """
    View individual sale details
    @login_required ensures user is authenticated before accessing
    """
    selected = get_object_or_404(Sale, id=product_id)
    form = SaleViewForm(instance=selected)
    context = {
        'selected': selected,
        'form': form
    }
    return render(request, 'view_sale.html', context)


# ====== BETTER APPROACH 2: Role-Based Access Control ======
def is_manager(user):
    """Check if user is in Manager group"""
    return user.groups.filter(name='Manager').exists()

def is_employee_or_manager(user):
    """Check if user is either Employee or Manager"""
    return user.groups.filter(name__in=['Manager', 'Employee']).exists()

@login_required
@user_passes_test(is_manager)  # Only managers can access
def managerOnlyView(request):
    """Example of manager-only view using proper decorators"""
    return render(request, 'manager_dashboard.html')

@login_required  
@user_passes_test(is_employee_or_manager)  # Both roles can access
def employeeAndManagerView(request):
    """Example of view accessible to both roles"""
    return render(request, 'general_dashboard.html')


# ====== BETTER APPROACH 3: Permission-Based Access ======
from django.contrib.auth.decorators import permission_required

@login_required
@permission_required('home.view_sale', raise_exception=True)
def viewSaleWithPermission(request, sale_id):
    """
    Uses Django's built-in permission system
    More granular than groups
    """
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'view_sale.html', {'sale': sale})


# ====== BETTER APPROACH 4: Class-Based Views with Mixins ======
from django.views.generic import DetailView

class SaleDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Class-based view with proper authentication mixins
    Much cleaner than function decorators for complex logic
    """
    model = Sale
    template_name = 'view_sale.html'
    context_object_name = 'sale'
    
    def test_func(self):
        """Define who can access this view"""
        return self.request.user.groups.filter(name__in=['Manager', 'Employee']).exists()
    
    def handle_no_permission(self):
        """Custom handling when user lacks permission"""
        messages.error(self.request, "You don't have permission to view this sale.")
        return redirect('dashboard')


# ====== WHY THESE ARE BETTER THAN REFERER CHECKING ======

"""
PROBLEMS WITH REFERER CHECKING:
❌ HTTP_REFERER can be:
   - Spoofed by malicious users
   - Stripped by browsers/privacy tools
   - Missing in legitimate scenarios (bookmarks, direct links)
   - Unreliable across different browsers

❌ Security issues:
   - Not a real authentication mechanism
   - Easy to bypass
   - Creates false sense of security

❌ User experience problems:
   - Breaks legitimate workflows
   - Prevents bookmarking
   - Confusing error messages


BENEFITS OF PROPER AUTHENTICATION:
✅ @login_required:
   - Built into Django
   - Reliable and tested
   - Works with sessions
   - Handles edge cases

✅ @user_passes_test:
   - Flexible role checking
   - Clear permission logic
   - Easy to test

✅ Permission system:
   - Granular control
   - Scalable
   - Industry standard

✅ Class-based mixins:
   - Reusable
   - Clean separation of concerns
   - Easy to extend
"""

# ====== SETTINGS CONFIGURATION ======
"""
In settings.py, add:

LOGIN_URL = '/login/'  # Where to redirect unauthenticated users
LOGIN_REDIRECT_URL = '/dashboard/'  # Where to go after login

This makes @login_required work properly without custom redirect logic.
"""