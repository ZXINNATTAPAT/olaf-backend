from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('blog.urls')),  
    path('api/auth/',include('authentication.urls' ,namespace='authentication')),
    path('sentry-debug/', trigger_error),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
