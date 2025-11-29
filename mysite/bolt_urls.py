"""
Django-Bolt URL configuration.
This integrates Django-Bolt API routes with Django's URL system.
"""
from django.urls import path, re_path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from blog import bolt_api as blog_api
from authentication import bolt_api as auth_api

# Create async view functions to mount BoltAPI instances
# BoltAPI uses async handlers, so we need to properly handle async/sync conversion

async def blog_api_handler(request):
    """Async handler for blog BoltAPI"""
    from django_bolt.responses import JSON
    
    # Extract path and method
    path_info = request.path_info
    method = request.method.lower()
    
    # Remove /api prefix to get relative path for the API
    api_path = path_info.replace('/api', '', 1) or '/'
    
    # Get the route handler from BoltAPI's internal routing
    # BoltAPI stores routes in _routes dict
    try:
        routes = blog_api.api._routes
        route_key = (method, api_path)
        
        # Try exact match first
        if route_key in routes:
            handler = routes[route_key]
            # Call the handler - it should be async
            result = await handler(request)
            # Handle different response types
            if isinstance(result, dict):
                return JsonResponse(result)
            elif hasattr(result, 'to_response'):
                return result.to_response()
            else:
                return JsonResponse({'data': result})
        
        # Try to find matching route (for path parameters)
        # This is simplified - BoltAPI may have more sophisticated routing
        for (route_method, route_path), handler in routes.items():
            if route_method == method:
                # Simple path matching (BoltAPI likely has better routing)
                if route_path == api_path or (route_path.endswith('}') and api_path.startswith(route_path.split('{')[0])):
                    result = await handler(request)
                    if isinstance(result, dict):
                        return JsonResponse(result)
                    elif hasattr(result, 'to_response'):
                        return result.to_response()
                    else:
                        return JsonResponse({'data': result})
        
        return JsonResponse({'error': 'Not found'}, status=404)
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

async def auth_api_handler(request):
    """Async handler for auth BoltAPI"""
    from django_bolt.responses import JSON
    
    path_info = request.path_info
    method = request.method.lower()
    api_path = path_info.replace('/api/auth', '', 1) or '/'
    
    try:
        routes = auth_api.api._routes
        route_key = (method, api_path)
        
        if route_key in routes:
            handler = routes[route_key]
            result = await handler(request)
            if isinstance(result, dict):
                return JsonResponse(result)
            elif hasattr(result, 'to_response'):
                return result.to_response()
            else:
                return JsonResponse({'data': result})
        
        # Try pattern matching
        for (route_method, route_path), handler in routes.items():
            if route_method == method:
                if route_path == api_path or (route_path.endswith('}') and api_path.startswith(route_path.split('{')[0])):
                    result = await handler(request)
                    if isinstance(result, dict):
                        return JsonResponse(result)
                    elif hasattr(result, 'to_response'):
                        return result.to_response()
                    else:
                        return JsonResponse({'data': result})
        
        return JsonResponse({'error': 'Not found'}, status=404)
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

# Convert async handlers to sync views for Django URL routing
@csrf_exempt
def blog_api_view(request):
    """Sync wrapper for blog API async handler"""
    return async_to_sync(blog_api_handler)(request)

@csrf_exempt
def auth_api_view(request):
    """Sync wrapper for auth API async handler"""
    return async_to_sync(auth_api_handler)(request)

# Mount Bolt APIs using regex patterns to catch all routes
urlpatterns = [
    # Mount blog API at /api/
    re_path(r'^api/.*$', blog_api_view),
    # Mount auth API at /api/auth/
    re_path(r'^api/auth/.*$', auth_api_view),
]

