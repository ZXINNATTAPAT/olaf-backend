"""
Custom middleware to prevent redirect loops for API endpoints
"""
from django.middleware.common import CommonMiddleware
from django.urls import resolve, Resolver404


class CustomCommonMiddleware(CommonMiddleware):
    """
    Custom CommonMiddleware that skips APPEND_SLASH redirect for API endpoints.
    This prevents redirect loops when DRF router already handles trailing slashes.
    """
    
    def process_request(self, request):
        # Skip APPEND_SLASH redirect for API endpoints
        if request.path_info.startswith('/api/'):
            # Check if the path resolves as-is
            try:
                resolve(request.path_info)
                # If it resolves, don't redirect
                return None
            except Resolver404:
                # If it doesn't resolve, still don't redirect for API endpoints
                # DRF router handles its own routing
                return None
        
        # For non-API requests, use the parent class behavior
        return super().process_request(request)

