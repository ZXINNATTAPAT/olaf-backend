from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Django-Bolt APIs (uncomment to enable Bolt APIs)
# Note: Bolt APIs will take precedence over DRF APIs at same paths
from mysite import bolt_urls as bolt_urls_config

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Django-Bolt APIs (uncomment to enable)
    # Uncomment the line below to use Bolt APIs instead of DRF
    # *bolt_urls_config.urlpatterns,
    
    # Django REST Framework APIs (default - keep for backward compatibility)
    path('api/', include('blog.urls')),  
    path('api/auth/',include('authentication.urls' ,namespace='authentication')),
    path('api/clouddiary/', include('clouddiary.urls', namespace='clouddiary')),
    path('api/shared-images/', include('shared_images.urls', namespace='shared_images'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
