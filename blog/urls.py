# from django.urls import include, path
# from rest_framework import routers
# from .views import UserViewSet, PostViewSet, CommentViewSet, PostLikeViewSet, CommentLikeViewSet, RegisterView, MyTokenObtainPairView, TokenRefreshView

# router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)
# router.register(r'posts', PostViewSet)
# router.register(r'comments', CommentViewSet)
# router.register(r'postlikes', PostLikeViewSet)
# router.register(r'commentlikes', CommentLikeViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
#     path('api/auth/register/', RegisterView.as_view(), name='register'),
#     path('api/auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
# ]
