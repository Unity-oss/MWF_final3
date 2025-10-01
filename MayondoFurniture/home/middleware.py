"""
Security Middleware for MWF Application
=====================================

This middleware adds security headers to all responses to prevent:
- Browser caching of sensitive pages
- Clickjacking attacks  
- XSS attacks
- Content type sniffing

Apply this by adding to MIDDLEWARE in settings.py
"""

class SecurityHeadersMiddleware:
    """
    Middleware that adds security headers to all responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only apply to authenticated pages
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Prevent caching
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            # Security headers
            response['X-Frame-Options'] = 'DENY'
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Clear site data on logout
            if 'logout' in request.path:
                response['Clear-Site-Data'] = '"cache", "cookies", "storage"'
                
        return response