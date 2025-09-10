from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .models import  Post, Comment, PostLike, CommentLike
from authentication.models import Account
from .serializers import UserSerializer, PostSerializer, CommentSerializer, PostLikeSerializer, CommentLikeSerializer
from shared_images.views import upload_image_to_object, get_object_images, get_primary_image, set_primary_image, delete_image
from authentication.authenticate import CustomAuthentication


class UserViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = UserSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('user').prefetch_related(
        'comments__user', 'likes__user', 'images'
    ).all()
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('user', 'post').prefetch_related('likes__user').all()
    serializer_class = CommentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    lookup_field = 'post_id'  # ใช้ 'post_id' ในการค้นหาไลค์

    def create(self, request):
        post_id = request.data.get('post')
        user_id = request.data.get('user', None)  # Allow anonymous likes

        post = Post.objects.get(pk=post_id)

        if user_id:
            user = Account.objects.get(pk=user_id)
            post_like, created = PostLike.objects.get_or_create(post=post, user=user)
            like_status = created
        else:
            # Handle anonymous like (e.g., increment a counter or track IPs)
            like_status = True  # Assume the like goes through

# Ensure like_count is updated correctly here
        like_count = post.like_count  # Call the like_count property
        return Response({
            'liked': like_status,
            'like_count': like_count  # Ensure like_count is included in response
        }, status=status.HTTP_201_CREATED if like_status else status.HTTP_200_OK)
    
    def destroy(self, request, post_id=None, user_id=None):
        try:
            # ค้นหาไลค์ที่ตรงกับ post_id และ user_id
            post_like = PostLike.objects.get(post_id=post_id, user_id=user_id)
            post_like.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except PostLike.DoesNotExist:
            return Response({'detail': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)
    
class CommentLikeViewSet(viewsets.ModelViewSet):
    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer
    lookup_field = 'comment_id'  # ใช้ 'comment_id' ในการค้นหาไลค์

    def create(self, request):
        comment_id = request.data.get('comment')
        user_id = request.data.get('user', None)  # Allow anonymous likes

        comment = Comment.objects.get(pk=comment_id)

        if user_id:
            user = Account.objects.get(pk=user_id)
            comment_like, created = CommentLike.objects.get_or_create(comment=comment, user=user)
            like_status = created
        else:
            # Handle anonymous like (e.g., increment a counter or track IPs)
            like_status = True  # Assume the like goes through
            # คุณอาจต้องการเพิ่มการจัดการสำหรับการไลค์แบบไม่ระบุชื่อ

        # อัปเดตจำนวนไลค์ในความคิดเห็น
        # comment.like_count = CommentLike.objects.filter(comment=comment).count()
        # comment.save()

        # Ensure like_count is updated correctly here
        like_count = comment.like_count  # Call the like_count property
        return Response({
            'liked': like_status,
            'like_count': like_count  # Ensure like_count is included in response
        }, status=status.HTTP_201_CREATED if like_status else status.HTTP_200_OK)

    def destroy(self, request, comment_id=None, user_id=None):
        try:
            # ค้นหาไลค์ที่ตรงกับ comment_id และ user_id
            comment_like = CommentLike.objects.get(comment_id=comment_id, user_id=user_id)
            comment_like.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except CommentLike.DoesNotExist:
            return Response({'detail': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)

# Image management endpoints for posts
@api_view(['POST'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def upload_post_image(request, post_id):
    """Upload an image to a specific post"""
    post = get_object_or_404(Post, pk=post_id)
    content_type = ContentType.objects.get_for_model(Post)
    return upload_image_to_object(request, content_type.id, post_id)

@api_view(['GET'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_post_images(request, post_id):
    """Get all images for a specific post"""
    post = get_object_or_404(Post, pk=post_id)
    content_type = ContentType.objects.get_for_model(Post)
    return get_object_images(request, content_type.id, post_id)

@api_view(['GET'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_post_primary_image(request, post_id):
    """Get the primary image for a specific post"""
    post = get_object_or_404(Post, pk=post_id)
    content_type = ContentType.objects.get_for_model(Post)
    return get_primary_image(request, content_type.id, post_id)

@api_view(['PATCH'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def set_post_primary_image(request, image_id):
    """Set an image as primary for its post"""
    return set_primary_image(request, image_id)

@api_view(['DELETE'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def delete_post_image(request, image_id):
    """Delete an image from a post"""
    return delete_image(request, image_id)

@api_view(['POST'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def add_post_image_path(request, post_id):
    """Add an image path to a post (for frontend-uploaded images)"""
    post = get_object_or_404(Post, pk=post_id)
    content_type = ContentType.objects.get_for_model(Post)
    
    # Use the shared images add_image_path_to_object function
    from shared_images.views import add_image_path_to_object
    return add_image_path_to_object(request, content_type.id, post_id)

@api_view(['POST'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def create_post_with_image(request):
    """Create a new post with image data from frontend"""
    from .serializers import PostSerializer
    from shared_images.serializers import SharedImagePathSerializer
    
    # Create the post first
    post_data = {
        'header': request.data.get('header'),
        'short': request.data.get('short'),
        'post_text': request.data.get('post_text'),
        'user_id': request.data.get('user_id')
    }
    
    post_serializer = PostSerializer(data=post_data)
    if not post_serializer.is_valid():
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    post = post_serializer.save()
    
    # Add image if provided
    if request.data.get('image_url'):
        image_data = {
            'image': request.data.get('image_url'),
            'caption': request.data.get('caption', ''),
            'is_primary': request.data.get('is_primary', True),
            'sort_order': request.data.get('sort_order', 0)
        }
        
        image_serializer = SharedImagePathSerializer(data=image_data)
        if image_serializer.is_valid():
            image_serializer.save(content_object=post)
        else:
            # If image fails, still return the post but with error info
            return Response({
                'post': PostSerializer(post).data,
                'image_error': image_serializer.errors
            }, status=status.HTTP_201_CREATED)
    
    # Return the complete post with images
    return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
