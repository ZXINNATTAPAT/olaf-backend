from django.urls import path
from . import views

app_name = "clouddiary"

urlpatterns = [
    # CloudDiary CRUD operations
    path('', views.CloudDiaryListCreateView.as_view(), name='clouddiary-list-create'),
    path('<int:pk>/', views.CloudDiaryDetailView.as_view(), name='clouddiary-detail'),
    path('my-diaries/', views.UserCloudDiaryListView.as_view(), name='user-clouddiary-list'),
    
    # Image operations
    path('<int:clouddiary_id>/images/', views.get_clouddiary_images, name='clouddiary-images'),
    path('<int:clouddiary_id>/add-image/', views.add_image_to_clouddiary, name='add-image'),
    path('images/<int:image_id>/delete/', views.delete_clouddiary_image, name='delete-image'),
]
