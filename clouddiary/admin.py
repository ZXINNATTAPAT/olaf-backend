from django.contrib import admin
from .models import CloudDiary, CloudDiaryImage

@admin.register(CloudDiary)
class CloudDiaryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_public', 'created_at', 'updated_at']
    list_filter = ['is_public', 'created_at', 'updated_at']
    search_fields = ['title', 'content', 'author__username', 'author__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(CloudDiaryImage)
class CloudDiaryImageAdmin(admin.ModelAdmin):
    list_display = ['clouddiary', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['clouddiary__title', 'caption']
    readonly_fields = ['uploaded_at', 'image_url', 'image_public_id', 'image_secure_url']
    ordering = ['-uploaded_at']