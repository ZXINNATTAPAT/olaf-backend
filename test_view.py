#!/usr/bin/env python3
"""
Test view for debugging
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def test_create_post(request):
    """Test view for creating post"""
    try:
        data = json.loads(request.body)
        return JsonResponse({
            'status': 'success',
            'message': 'Test endpoint working',
            'received_data': data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

# Test the function directly
if __name__ == "__main__":
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.post('/test/', 
        data=json.dumps({'header': 'test'}),
        content_type='application/json'
    )
    
    response = test_create_post(request)
    print(f"Status: {response.status_code}")
    print(f"Content: {response.content.decode()}")
