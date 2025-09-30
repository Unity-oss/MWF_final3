"""
Context Processors for Mayondo Furniture Management System
========================================================

This file contains context processors that make variables available
globally across all templates in the application.
"""

def user_roles(request):
    """
    Context processor to make user role information available in all templates.
    
    Returns:
        dict: Contains is_manager and is_employee boolean flags
    """
    context = {
        'is_manager': False,
        'is_employee': False,
    }
    
    if request.user.is_authenticated:
        context['is_manager'] = request.user.groups.filter(name="Manager").exists()
        context['is_employee'] = request.user.groups.filter(name="Employee").exists()
    
    return context