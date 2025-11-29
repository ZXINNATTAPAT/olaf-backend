"""
Django-Bolt API routes for blog endpoints.
This replaces the DRF ViewSets with high-performance Bolt routes.
"""
from django_bolt import BoltAPI
from django_bolt.serializers import Serializer, Nested
from django_bolt.responses import JSON, Response
from typing import Annotated, Optional
from msgspec import Meta
from .models import Post, Comment, PostLike, CommentLike
from authentication.models import Account
from shared_images.serializers import SharedImageSerializer

# Initialize Bolt API
api = BoltAPI()

# Serializers
class UserSerializer(Serializer):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: str
    created_at: str

class CommentSerializer(Serializer):
    comment_id: int
    post: int
    user: Annotated[UserSerializer, Nested(UserSerializer)]
    comment_datetime: str
    comment_text: str
    like_count: int

class PostSerializer(Serializer):
    post_id: int
    post_text: str
    post_datetime: str
    user: Annotated[UserSerializer, Nested(UserSerializer)]
    header: Optional[str] = None
    short: Optional[str] = None
    like_count: int
    comment_count: int
    liked: bool
    image_url: Optional[str] = None
    image_secure_url: Optional[str] = None
    primary_image_url: Optional[str] = None
    image_count: int

# API Routes
@api.get("/posts")
async def list_posts(page: int = 1, page_size: int = 20):
    """List all posts with pagination"""
    offset = (page - 1) * page_size
    posts = await Post.objects.select_related('user').prefetch_related(
        'comments__user', 'likes__user', 'images'
    ).order_by('-post_datetime')[offset:offset + page_size]
    
    results = []
    async for post in posts:
        results.append({
            "post_id": post.post_id,
            "post_text": post.post_text,
            "post_datetime": post.post_datetime.isoformat(),
            "user": {
                "id": post.user.id,
                "username": post.user.username,
                "email": post.user.email,
            },
            "header": post.header,
            "short": post.short,
            "like_count": post.like_count,
            "comment_count": post.comments.count(),
            "liked": False,  # TODO: Check if current user liked
            "image_url": post.primary_image_url,
            "image_secure_url": post.primary_image_url,
            "primary_image_url": post.primary_image_url,
            "image_count": post.image_count,
        })
    
    return {
        "count": await Post.objects.acount(),
        "next": f"/api/posts?page={page + 1}" if len(results) == page_size else None,
        "previous": f"/api/posts?page={page - 1}" if page > 1 else None,
        "results": results
    }

@api.get("/posts/{post_id}")
async def get_post(post_id: int):
    """Get a single post by ID"""
    try:
        post = await Post.objects.select_related('user').prefetch_related(
            'comments__user', 'likes__user', 'images'
        ).aget(post_id=post_id)
        
        return {
            "post_id": post.post_id,
            "post_text": post.post_text,
            "post_datetime": post.post_datetime.isoformat(),
            "user": {
                "id": post.user.id,
                "username": post.user.username,
                "email": post.user.email,
            },
            "header": post.header,
            "short": post.short,
            "like_count": post.like_count,
            "comment_count": post.comments.count(),
            "liked": False,  # TODO: Check if current user liked
            "image_url": post.primary_image_url,
            "image_secure_url": post.primary_image_url,
            "primary_image_url": post.primary_image_url,
            "image_count": post.image_count,
        }
    except Post.DoesNotExist:
        return JSON({"error": "Post not found"}, status_code=404)

@api.post("/posts")
async def create_post(
    header: Optional[str] = None,
    short: Optional[str] = None,
    post_text: str = "",
    user_id: int = 0,
):
    """Create a new post"""
    # TODO: Get user from authentication
    user = await Account.objects.aget(id=user_id)
    
    post = await Post.objects.acreate(
        header=header,
        short=short,
        post_text=post_text,
        user=user
    )
    
    return {
        "post_id": post.post_id,
        "post_text": post.post_text,
        "post_datetime": post.post_datetime.isoformat(),
        "user": {
            "id": post.user.id,
            "username": post.user.username,
            "email": post.user.email,
        },
        "header": post.header,
        "short": post.short,
        "like_count": 0,
        "comment_count": 0,
        "liked": False,
    }

