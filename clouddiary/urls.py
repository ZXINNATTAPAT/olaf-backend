from django.urls import path
from . import views

app_name = "clouddiary"

urlpatterns = [
    # CloudDiary CRUD operations
    path('', views.CloudDiaryListCreateView.as_view(), name='clouddiary-list-create'),
    path('<int:pk>/', views.CloudDiaryDetailView.as_view(), name='clouddiary-detail'),
    path('my-diaries/', views.UserCloudDiaryListView.as_view(), name='user-clouddiary-list'),
    
    # Old image operations (for backward compatibility)
    path('<int:clouddiary_id>/images/', views.get_clouddiary_images, name='clouddiary-images'),
    path('<int:clouddiary_id>/add-image/', views.add_image_to_clouddiary, name='add-image'),
    path('images/<int:image_id>/delete/', views.delete_clouddiary_image, name='delete-image'),
    
    # New shared image operations
    path('<int:clouddiary_id>/upload-shared-image/', views.upload_clouddiary_image, name='upload-clouddiary-shared-image'),
    path('<int:clouddiary_id>/add-image-path/', views.add_clouddiary_image_path, name='add-clouddiary-image-path'),
    path('<int:clouddiary_id>/shared-images/', views.get_clouddiary_shared_images, name='get-clouddiary-shared-images'),
    path('<int:clouddiary_id>/primary-shared-image/', views.get_clouddiary_primary_shared_image, name='get-clouddiary-primary-shared-image'),
    path('shared-images/<int:image_id>/set-primary/', views.set_clouddiary_primary_image, name='set-clouddiary-primary-image'),
    path('shared-images/<int:image_id>/delete/', views.delete_clouddiary_shared_image, name='delete-clouddiary-shared-image'),
]
