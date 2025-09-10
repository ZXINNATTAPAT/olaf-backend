from django.urls import path
from . import views

app_name = "shared_images"

urlpatterns = [
    # Image management for specific objects
    path('objects/<int:content_type_id>/<int:object_id>/', 
         views.SharedImageListCreateView.as_view(), 
         name='object-images-list-create'),
    
    # Individual image operations
    path('images/<int:pk>/', 
         views.SharedImageDetailView.as_view(), 
         name='image-detail'),
    
    # Specific image operations
    path('upload/<int:content_type_id>/<int:object_id>/', 
         views.upload_image_to_object, 
         name='upload-image'),
    
    # New endpoint for frontend-uploaded images (path only)
    path('add-path/<int:content_type_id>/<int:object_id>/', 
         views.add_image_path_to_object, 
         name='add-image-path'),
    
    path('objects/<int:content_type_id>/<int:object_id>/list/', 
         views.get_object_images, 
         name='get-object-images'),
    
    path('objects/<int:content_type_id>/<int:object_id>/primary/', 
         views.get_primary_image, 
         name='get-primary-image'),
    
    path('images/<int:image_id>/set-primary/', 
         views.set_primary_image, 
         name='set-primary-image'),
    
    path('images/<int:image_id>/delete/', 
         views.delete_image, 
         name='delete-image'),
]
