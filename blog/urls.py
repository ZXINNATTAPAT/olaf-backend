from django.urls import include, path
from rest_framework import routers
from .views import UserViewSet, PostViewSet, CommentViewSet, PostLikeViewSet, CommentLikeViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'postlikes', PostLikeViewSet)
router.register(r'commentlikes', CommentLikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
