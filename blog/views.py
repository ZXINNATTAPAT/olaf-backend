from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .models import User, Post, Comment, PostLike, CommentLike
from .serializers import UserSerializer, PostSerializer, CommentSerializer, PostLikeSerializer, CommentLikeSerializer, RegisterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer

class CommentLikeViewSet(viewsets.ModelViewSet):
    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    pass

class UserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
