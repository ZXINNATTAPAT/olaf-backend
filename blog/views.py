from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import  Post, Comment, PostLike, CommentLike
from authentication.models import Account
from .serializers import UserSerializer, PostSerializer, PostFeedSerializer, CommentSerializer, PostLikeSerializer, CommentLikeSerializer
from shared_images.views import upload_image_to_object, get_object_images, get_primary_image, set_primary_image, delete_image
from authentication.authenticate import CustomAuthentication


class UserViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = UserSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('user').prefetch_related(
        'comments__user', 'likes__user', 'images'
    ).order_by('-post_datetime')
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
    
    def list(self, request, *args, **kwargs):
        """List posts - use PostSerializer by default"""
        return super().list(request, *args, **kwargs)

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

@api_view(['GET'])
@csrf_exempt
@authentication_classes([])  # No authentication required
@permission_classes([permissions.AllowAny])  # Allow any user (including anonymous)
def post_feed(request):
    """Get posts feed - lightweight version without post_text and comments
    This endpoint does not require CSRF token or authentication."""
    from rest_framework.pagination import PageNumberPagination
    from django.db.models import Count, OuterRef, Exists
    from .models import PostLike
    
    # Get pagination parameters
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    
    # Get queryset
    # Optimize: Remove 'likes__user' prefetch as it's expensive and likely unused by FeedSerializer
    # Add annotations for counts to avoid N+1 queries
    queryset = Post.objects.select_related('user').prefetch_related(
        'images'
    ).annotate(
        annotated_like_count=Count('likes', distinct=True),
        annotated_comment_count=Count('comments', distinct=True),
        annotated_image_count=Count('images', distinct=True)
    ).order_by('-post_datetime')
    
    # Annotate is_liked if user is authenticated
    if request.user.is_authenticated:
        is_liked = PostLike.objects.filter(
            post=OuterRef('pk'),
            user=request.user
        )
        queryset = queryset.annotate(is_liked=Exists(is_liked))
    
    # Manual pagination
    paginator = PageNumberPagination()
    paginator.page_size = page_size
    paginator.page_size_query_param = 'page_size'
    paginator.max_page_size = 100
    
    page_obj = paginator.paginate_queryset(queryset, request)
    
    # Serialize with PostFeedSerializer
    serializer = PostFeedSerializer(page_obj, many=True, context={'request': request})
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['POST'])
@authentication_classes([CustomAuthentication])
@permission_classes([permissions.IsAuthenticated])
def create_post_with_image(request):
    """Create a new post with image data from frontend"""
    import logging
    logger = logging.getLogger(__name__)
    
    from .serializers import PostSerializer
    from shared_images.serializers import SharedImagePathSerializer
    
    # Log authentication status and cookies for debugging
    all_cookies = dict(request.COOKIES)
    logger.info(f"📝 Create post request - Cookies received: {list(all_cookies.keys())}")
    logger.info(f"📝 User authenticated: {request.user.is_authenticated if request.user else False}")
    logger.info(f"📝 User: {request.user.email if request.user and hasattr(request.user, 'email') else 'None'}")
    logger.info(f"📝 Request origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    
    # Check if user is authenticated
    if not request.user or not request.user.is_authenticated:
        logger.warning(f"❌ Authentication failed - No user or not authenticated. Cookies: {list(all_cookies.keys())}")
        return Response(
            {'error': 'Authentication required', 'detail': 'No valid authentication token found. Please login again.'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Create the post first - use authenticated user instead of user_id from request
    post_data = {
        'header': request.data.get('header'),
        'short': request.data.get('short'),
        'post_text': request.data.get('post_text'),
        'user_id': request.user.id  # Use authenticated user
    }
    
    post_serializer = PostSerializer(data=post_data, context={'request': request})
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
                'post': PostSerializer(post, context={'request': request}).data,
                'image_error': image_serializer.errors
            }, status=status.HTTP_201_CREATED)
    
    # Return the complete post with images
    response = Response(
        PostSerializer(post, context={'request': request}).data, 
        status=status.HTTP_201_CREATED
    )
    
    # Ensure CORS headers are set
    origin = request.META.get('HTTP_ORIGIN')
    if origin and origin in settings.CORS_ALLOWED_ORIGINS:
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Credentials"] = "true"
    
    return response
