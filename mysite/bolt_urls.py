"""
Django-Bolt URL configuration.
This integrates Django-Bolt API routes with Django's URL system.
"""
from django.urls import path, re_path
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from blog import bolt_api as blog_api
from authentication import bolt_api as auth_api
from clouddiary import bolt_api as clouddiary_api
import re
import inspect
import json
from typing import get_origin, get_args, Union
from django_bolt.responses import JSON

# Special marker class to indicate route should fall through to DRF
class FallThroughToDRF:
    pass

def extract_handler_params(handler, request, path_params=None):
    """Extract parameters for BoltAPI handler from Django request"""
    sig = inspect.signature(handler)
    bound_params = {}
    
    # Add path parameters first
    if path_params:
        bound_params.update(path_params)
    
    # Check if handler needs request object
    if 'request' in sig.parameters and 'request' not in bound_params:
        bound_params['request'] = request
    
    # Extract query parameters
    for param_name, param in sig.parameters.items():
        if param_name in bound_params:
            continue  # Already set from path params or request
            
        if param_name in request.GET:
            param_value = request.GET[param_name]
            # Convert to appropriate type
            try:
                # Check for Optional types (Union with None)
                origin = get_origin(param.annotation)
                args = get_args(param.annotation) if origin else ()
                
                # Handle Optional[int], Optional[float], etc.
                if origin is Union:
                    # Optional is Union[Type, None], get the actual type
                    non_none_types = [arg for arg in args if arg is not type(None)]
                    if non_none_types:
                        actual_type = non_none_types[0]
                        if actual_type == int:
                            bound_params[param_name] = int(param_value)
                        elif actual_type == float:
                            bound_params[param_name] = float(param_value)
                        elif actual_type == bool:
                            bound_params[param_name] = param_value.lower() in ('true', '1', 'yes')
                        else:
                            bound_params[param_name] = param_value
                    else:
                        bound_params[param_name] = param_value
                elif param.annotation == int:
                    bound_params[param_name] = int(param_value)
                elif param.annotation == float:
                    bound_params[param_name] = float(param_value)
                elif param.annotation == bool:
                    bound_params[param_name] = param_value.lower() in ('true', '1', 'yes')
                else:
                    bound_params[param_name] = param_value
            except (ValueError, TypeError) as e:
                # If conversion fails, skip this parameter or use default
                if param.default != inspect.Parameter.empty:
                    bound_params[param_name] = param.default
                # If no default and it's Optional, set to None
                elif origin is Union and type(None) in args:
                    bound_params[param_name] = None
        elif param.default != inspect.Parameter.empty:
            # Use default value
            bound_params[param_name] = param.default
    
    # For POST/PUT/PATCH, try to get request body
    if request.method in ('POST', 'PUT', 'PATCH') and request.body:
        try:
            body_data = json.loads(request.body)
            # Check if handler expects a data parameter (like LoginSerializer)
            for param_name, param in sig.parameters.items():
                if param_name == 'data' and param_name not in bound_params:
                    # Try to instantiate the serializer type
                    param_type = param.annotation
                    if hasattr(param_type, '__call__'):
                        try:
                            bound_params[param_name] = param_type(**body_data)
                        except:
                            bound_params[param_name] = body_data
                    else:
                        bound_params[param_name] = body_data
        except:
            pass
    
    return bound_params

async def blog_api_handler(request):
    """Async handler for blog BoltAPI"""
    # Extract path and method
    path_info = request.path_info
    method = request.method.upper()
    
    # Skip routes that should be handled by DRF (must come before Bolt patterns)
    # These routes are explicitly handled by DRF in urls.py
    if path_info.startswith('/api/posts/feed') or path_info.startswith('/api/posts/create-with-image'):
        return FallThroughToDRF()
    
    # Remove /api prefix to get relative path for the API
    api_path = path_info.replace('/api', '', 1) or '/'
    # Remove trailing slash for matching (Bolt routes don't have trailing slashes)
    if api_path != '/' and api_path.endswith('/'):
        api_path = api_path[:-1]
    
    # Get the route handler from BoltAPI's internal routing
    # BoltAPI stores routes as list of tuples: (method, path, index, handler)
    try:
        routes = blog_api.api._routes
        
        # Try to find matching route
        matched = False
        for route_method, route_path, _, handler in routes:
            if route_method != method:
                continue
            
            path_params = None
            
            # Try exact match first
            if route_path == api_path:
                matched = True
            # Try pattern matching for path parameters (e.g., /posts/{post_id})
            elif '{' in route_path:
                # Convert route_path to regex pattern
                pattern = route_path.replace('{', '(?P<').replace('}', '>[^/]+)')
                match = re.match(f'^{pattern}$', api_path)
                if match:
                    matched = True
                    # Extract path parameters
                    params = match.groupdict()
                    if params:
                        # Convert string params to appropriate types based on handler signature
                        sig = inspect.signature(handler)
                        path_params = {}
                        for param_name, param_value in params.items():
                            if param_name in sig.parameters:
                                param_type = sig.parameters[param_name].annotation
                                if param_type == int:
                                    path_params[param_name] = int(param_value)
                                elif param_type == float:
                                    path_params[param_name] = float(param_value)
                                else:
                                    path_params[param_name] = param_value
                else:
                    continue  # Pattern doesn't match
            else:
                continue  # No match
            
            # If we found a match, handle the request
            if matched:
                # Extract all parameters (path + query + body)
                bound_params = extract_handler_params(handler, request, path_params)
                
                # Call handler with bound parameters
                result = await handler(**bound_params)
                
                if isinstance(result, dict):
                    return JsonResponse(result)
                elif hasattr(result, 'to_response'):
                    return result.to_response()
                else:
                    return JsonResponse({'data': result})
        
        # If no route matched, return FallThroughToDRF to let Django try other URL patterns (DRF routes)
        return FallThroughToDRF()
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

async def auth_api_handler(request):
    """Async handler for auth BoltAPI"""
    path_info = request.path_info
    method = request.method.upper()
    api_path = path_info.replace('/api/auth', '', 1) or '/'
    # Remove trailing slash for matching (Bolt routes don't have trailing slashes)
    if api_path != '/' and api_path.endswith('/'):
        api_path = api_path[:-1]
    
    try:
        routes = auth_api.api._routes
        
        # Try to find matching route
        for route_method, route_path, _, handler in routes:
            if route_method != method:
                continue
            
            path_params = None
            
            # Try exact match first
            if route_path == api_path:
                pass  # No path params
            # Try pattern matching for path parameters
            elif '{' in route_path:
                pattern = route_path.replace('{', '(?P<').replace('}', '>[^/]+)')
                match = re.match(f'^{pattern}$', api_path)
                if not match:
                    continue  # Pattern doesn't match
                
                # Extract path parameters
                params = match.groupdict()
                if params:
                    sig = inspect.signature(handler)
                    path_params = {}
                    for param_name, param_value in params.items():
                        if param_name in sig.parameters:
                            param_type = sig.parameters[param_name].annotation
                            if param_type == int:
                                path_params[param_name] = int(param_value)
                            elif param_type == float:
                                path_params[param_name] = float(param_value)
                            else:
                                path_params[param_name] = param_value
            else:
                continue  # No match
            
            # Extract all parameters (path + query + body)
            bound_params = extract_handler_params(handler, request, path_params)
            
            # Call handler with bound parameters
            result = await handler(**bound_params)
            
            if isinstance(result, JSON):
                # Handle Bolt JSON response object explicitly
                # It has .body (or .data/content depending on impl) and .status_code
                # Based on usage in bolt_api.py: JSON(data, status_code=...)
                # It likely stores data in a way that we can extract or invalidating JsonResponse
                # Assuming it has a way to get dict content. If it's the class from django_bolt,
                # we should check its attributes.
                # Usually .body or ._content. msgspec structs/json usually need serialization.
                # Safest is to try getattr.
                data = getattr(result, 'body', getattr(result, 'content', None))
                # If body/content is bytes/string, parse it? No, JSON() usually takes dict.
                # Let's assume it behaves like a response holder.
                # If result is not serializable, we should look at its structure.
                # For now, let's assume result itself is not the dict, but result.body is.
                # But wait, looking at bolt_api.py: JSON({"error":...}, status_code=400)
                # It passes dict as first arg.
                return JsonResponse(result.body if hasattr(result, 'body') else result, status=result.status_code, safe=False)
            elif isinstance(result, dict):
                return JsonResponse(result)
            elif hasattr(result, 'to_response'):
                return result.to_response()
            else:
                return JsonResponse({'data': result})
        
        return JsonResponse({'error': 'Not found', 'path': api_path, 'method': method}, status=404)
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

# Convert async handlers to sync views for Django URL routing
@csrf_exempt
def blog_api_view(request):
    """Sync wrapper for blog API async handler"""
    # Check if this path should be handled by DRF first
    path_info = request.path_info
    if path_info.startswith('/api/posts/feed') or path_info.startswith('/api/posts/create-with-image'):
        # Let Django try other URL patterns (DRF routes)
        raise Http404("Route handled by DRF")
    
    try:
        result = async_to_sync(blog_api_handler)(request)
        # If handler returns FallThroughToDRF, it means no route matched - let Django try other patterns
        if isinstance(result, FallThroughToDRF):
            raise Http404("Route not found in Bolt API")
        return result
    except Http404:
        # Re-raise Http404 to let Django try other URL patterns
        raise
    except Exception as e:
        # For other exceptions, return error response
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

@csrf_exempt
def auth_api_view(request):
    """Sync wrapper for auth API async handler"""
    return async_to_sync(auth_api_handler)(request)

async def clouddiary_api_handler(request):
    """Async handler for CloudDiary BoltAPI"""
    path_info = request.path_info
    method = request.method.upper()
    api_path = path_info.replace('/api/clouddiary', '', 1) or '/'
    # Remove trailing slash for matching
    if api_path != '/' and api_path.endswith('/'):
        api_path = api_path[:-1]
    
    try:
        routes = clouddiary_api.api._routes
        
        matched = False
        for route_method, route_path, _, handler in routes:
            if route_method != method:
                continue
            
            path_params = None
            
            if route_path == api_path:
                matched = True
            elif '{' in route_path:
                pattern = route_path.replace('{', '(?P<').replace('}', '>[^/]+)')
                match = re.match(f'^{pattern}$', api_path)
                if match:
                    matched = True
                    params = match.groupdict()
                    if params:
                        sig = inspect.signature(handler)
                        path_params = {}
                        for param_name, param_value in params.items():
                            if param_name in sig.parameters:
                                param_type = sig.parameters[param_name].annotation
                                if param_type == int:
                                    path_params[param_name] = int(param_value)
                                elif param_type == float:
                                    path_params[param_name] = float(param_value)
                                else:
                                    path_params[param_name] = param_value
                else:
                    continue
            else:
                continue
            
            if matched:
                bound_params = extract_handler_params(handler, request, path_params)
                result = await handler(**bound_params)
                
                if isinstance(result, dict):
                    return JsonResponse(result)
                elif hasattr(result, 'to_response'):
                    return result.to_response()
                else:
                    return JsonResponse({'data': result})
        
        return FallThroughToDRF()
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

@csrf_exempt
def clouddiary_api_view(request):
    """Sync wrapper for CloudDiary API async handler"""
    try:
        result = async_to_sync(clouddiary_api_handler)(request)
        if isinstance(result, FallThroughToDRF):
            raise Http404("Route not found in Bolt API")
        return result
    except Http404:
        raise
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)

# Swagger/OpenAPI documentation endpoints
# Use BoltAPI.view() to create Swagger UI endpoint
from blog import bolt_api as blog_api

@csrf_exempt
def swagger_ui(request):
    """Swagger UI for API documentation"""
    # BoltAPI.view() is not async, it's a decorator method
    # For now, return a simple message or redirect to OpenAPI schema
    # The actual Swagger UI should be served by BoltAPI's built-in routes
    return JsonResponse({
        "message": "Swagger UI",
        "openapi_schema": "/api/openapi.json",
        "note": "Use /api/openapi.json for OpenAPI schema"
    })

@csrf_exempt
def openapi_schema(request):
    """OpenAPI schema JSON endpoint"""
    schema = blog_api.api._get_openapi_schema()
    return JsonResponse(schema)

# Mount Bolt APIs using regex patterns to catch all routes
# IMPORTANT: More specific patterns must come first
urlpatterns = [
    # Swagger/OpenAPI documentation
    # BoltAPI automatically serves OpenAPI at /schema (configured in OpenAPIConfig)
    path('api/docs/', swagger_ui, name='swagger-ui'),
    path('api/openapi.json', openapi_schema, name='openapi-schema'),
    # /api/schema is handled by blog_api_view regex pattern below
    
    # Mount CloudDiary API at /api/clouddiary/ (most specific)
    re_path(r'^api/clouddiary/.*$', clouddiary_api_view),
    # Mount auth API at /api/auth/ (more specific, must come before blog)
    # Disabled to ensure DRF handles auth (Login/Refresh with Cookies)
    # re_path(r'^api/auth/.*$', auth_api_view),
    # Mount blog API at /api/ (less specific, comes after auth and clouddiary)
    # This will also handle OpenAPI routes registered by BoltAPI
    # Exclude /api/auth/ so it falls through to DRF implemented in urls.py
    re_path(r'^api/(?!auth/).*$', blog_api_view),
]
