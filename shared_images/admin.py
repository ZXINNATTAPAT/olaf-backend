from django.contrib import admin
from .models import SharedImage

@admin.register(SharedImage)
class SharedImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_object', 'caption', 'is_primary', 'sort_order', 'uploaded_at']
    list_filter = ['is_primary', 'content_type', 'uploaded_at']
    search_fields = ['caption', 'content_object']
    list_editable = ['is_primary', 'sort_order']
    ordering = ['-uploaded_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('content_type')