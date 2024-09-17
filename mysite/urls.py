from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from blog.views import UserViewSet, PostViewSet, CommentViewSet, PostLikeViewSet, CommentLikeViewSet, RegisterView, MyTokenObtainPairView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'postlikes', PostLikeViewSet)
router.register(r'commentlikes', CommentLikeViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI2NTczNDgzLCJpYXQiOjE3MjY1NzMxODMsImp0aSI6ImYyM2E5NTBlZTk0YjQ1OThiODY1ZTE2MjYwMjI4ZTdmIiwidXNlcl9pZCI6Mn0.RyWVdGBPeiXTiBOl9B69NGOzFGZL0pfOW6FNBsjko6M