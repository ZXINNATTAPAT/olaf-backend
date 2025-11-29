from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Django-Bolt APIs (uncomment to enable Bolt APIs)
# Note: Bolt APIs will take precedence over DRF APIs at same paths
from mysite import bolt_urls as bolt_urls_config
# Import DRF views directly for routes that Bolt doesn't handle
from blog.views import post_feed, create_post_with_image

urlpatterns = [
    # Django Admin removed - using Swagger/OpenAPI documentation instead
    # Access API docs at: /api/docs/
    
    # Django REST Framework APIs - specific routes that Bolt doesn't handle
    # These MUST come BEFORE Bolt regex patterns to take precedence
    # Use exact path() instead of regex to ensure they match first
    path('api/posts/feed/', post_feed, name='post-feed'),  # Feed endpoint
    path('api/posts/create-with-image/', create_post_with_image, name='create-post-with-image'),  # Custom endpoint
    path('api/shared-images/', include('shared_images.urls', namespace='shared_images')),
    
    # Django-Bolt APIs (enabled - handles /api/posts and /api/auth)
    # Note: Bolt regex patterns will match /api/* but specific paths above take precedence
    *bolt_urls_config.urlpatterns,
    
    # DRF blog and auth as fallback for other routes not handled by Bolt
    # These come after Bolt patterns, so Bolt routes take precedence
    path('api/', include('blog.urls')),  
    path('api/auth/',include('authentication.urls' ,namespace='authentication')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
