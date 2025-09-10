from django.urls import include, path
from rest_framework import routers
from .views import (
    UserViewSet, PostViewSet, CommentViewSet, PostLikeViewSet, CommentLikeViewSet,
    upload_post_image, get_post_images, get_post_primary_image, 
    set_post_primary_image, delete_post_image, add_post_image_path, create_post_with_image
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'postlikes', PostLikeViewSet)
router.register(r'commentlikes', CommentLikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('postlikes/<int:post_id>/<int:user_id>/', PostLikeViewSet.as_view({'delete': 'destroy'}), name='postlike'),
    path('commentlikes/<int:comment_id>/<int:user_id>/', CommentLikeViewSet.as_view({'delete': 'destroy'}), name='commentlike'),
    
    # Post creation with image
    path('posts/create-with-image/', create_post_with_image, name='create-post-with-image'),
    
    # Image management endpoints
    path('posts/<int:post_id>/upload-image/', upload_post_image, name='upload-post-image'),
    path('posts/<int:post_id>/add-image-path/', add_post_image_path, name='add-post-image-path'),
    path('posts/<int:post_id>/images/', get_post_images, name='get-post-images'),
    path('posts/<int:post_id>/primary-image/', get_post_primary_image, name='get-post-primary-image'),
    path('images/<int:image_id>/set-primary/', set_post_primary_image, name='set-post-primary-image'),
    path('images/<int:image_id>/delete/', delete_post_image, name='delete-post-image'),
]
