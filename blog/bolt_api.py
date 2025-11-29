"""
Django-Bolt API routes for blog endpoints.
This replaces the DRF ViewSets with high-performance Bolt routes.
"""
from django_bolt import BoltAPI
from django_bolt.serializers import Serializer, Nested
from django_bolt.responses import JSON, Response
from typing import Annotated, Optional
from msgspec import Meta
from asgiref.sync import sync_to_async
from .models import Post, Comment, PostLike, CommentLike
from authentication.models import Account
from shared_images.serializers import SharedImageSerializer

# Initialize Bolt API with OpenAPI/Swagger configuration
from django_bolt import OpenAPIConfig

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="Olaf Backend API",
        version="1.0.0",
        description="High-performance API for Olaf social media platform",
        servers=[
            {"url": "http://localhost:8000", "description": "Development server"},
            {"url": "https://web-production-ba20a.up.railway.app", "description": "Production server"},
        ],
    ),
)

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
async def list_posts(page: int = 1, page_size: int = 20, limit: Optional[int] = None, user: Optional[int] = None):
    """List all posts with pagination"""
    # Support 'limit' as alias for 'page_size'
    if limit is not None:
        page_size = limit
    
    offset = (page - 1) * page_size
    
    # Build queryset
    queryset = Post.objects.select_related('user').prefetch_related(
        'comments__user', 'likes__user', 'images'
    )
    
    # Filter by user if provided
    if user is not None:
        queryset = queryset.filter(user_id=user)
    
    # Apply ordering
    queryset = queryset.order_by('-post_datetime')
    
    # Get total count before slicing
    total_count = await queryset.acount()
    
    # Apply pagination slicing
    posts_queryset = queryset[offset:offset + page_size]
    
    results = []
    async for post in posts_queryset:
        # comment_count is a synchronous operation, wrap it
        comment_count = await sync_to_async(lambda: post.comments.count())()
        
        # Get image properties (these are synchronous, need to wrap)
        def get_image_props():
            return {
                "primary_image_url": post.primary_image_url,
                "image_count": post.image_count,
            }
        
        image_props = await sync_to_async(get_image_props)()
        
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
            "comment_count": comment_count,
            "liked": False,  # TODO: Check if current user liked
            "image_url": image_props["primary_image_url"],
            "image_secure_url": image_props["primary_image_url"],
            "primary_image_url": image_props["primary_image_url"],
            "image_count": image_props["image_count"],
        })
    
    # Build query string for pagination links
    query_params = []
    if user is not None:
        query_params.append(f"user={user}")
    if limit is not None:
        query_params.append(f"limit={limit}")
    else:
        query_params.append(f"page_size={page_size}")
    query_string = "&".join(query_params)
    prefix = f"?{query_string}&" if query_string else "?"
    
    return {
        "count": total_count,
        "next": f"/api/posts{prefix}page={page + 1}" if len(results) == page_size else None,
        "previous": f"/api/posts{prefix}page={page - 1}" if page > 1 else None,
        "results": results
    }

@api.get("/posts/{post_id}")
async def get_post(post_id: int):
    """Get a single post by ID"""
    try:
        post = await Post.objects.select_related('user').prefetch_related(
            'comments__user', 'likes__user', 'images'
        ).aget(post_id=post_id)
        
        # comment_count is a synchronous operation, wrap it
        comment_count = await sync_to_async(lambda: post.comments.count())()
        
        # Get image properties (these are synchronous, need to wrap)
        def get_image_props():
            return {
                "primary_image_url": post.primary_image_url,
                "image_count": post.image_count,
            }
        
        image_props = await sync_to_async(get_image_props)()
        
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
            "comment_count": comment_count,
            "liked": False,  # TODO: Check if current user liked
            "image_url": image_props["primary_image_url"],
            "image_secure_url": image_props["primary_image_url"],
            "primary_image_url": image_props["primary_image_url"],
            "image_count": image_props["image_count"],
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

# Comments endpoints
@api.get("/comments")
async def list_comments(post: Optional[int] = None):
    """List comments, optionally filtered by post"""
    if post:
        comments = Comment.objects.select_related('user', 'post').prefetch_related('likes__user').filter(post_id=post)
    else:
        comments = Comment.objects.select_related('user', 'post').prefetch_related('likes__user').all()
    
    results = []
    async for comment in comments:
        like_count = await sync_to_async(lambda: comment.like_count)()
        results.append({
            "comment_id": comment.comment_id,
            "post": comment.post.post_id,
            "user": {
                "id": comment.user.id,
                "username": comment.user.username,
                "email": comment.user.email,
            },
            "comment_datetime": comment.comment_datetime.isoformat(),
            "comment_text": comment.comment_text,
            "like_count": like_count,
        })
    
    return {"results": results}

@api.get("/comments/{comment_id}")
async def get_comment(comment_id: int):
    """Get a single comment by ID"""
    try:
        comment = await Comment.objects.select_related('user', 'post').prefetch_related('likes__user').aget(comment_id=comment_id)
        like_count = await sync_to_async(lambda: comment.like_count)()
        
        return {
            "comment_id": comment.comment_id,
            "post": comment.post.post_id,
            "user": {
                "id": comment.user.id,
                "username": comment.user.username,
                "email": comment.user.email,
            },
            "comment_datetime": comment.comment_datetime.isoformat(),
            "comment_text": comment.comment_text,
            "like_count": like_count,
        }
    except Comment.DoesNotExist:
        return JSON({"error": "Comment not found"}, status_code=404)

class CreateCommentSerializer(Serializer):
    post: int
    user_id: int
    comment_text: str

@api.post("/comments")
async def create_comment(data: CreateCommentSerializer):
    """Create a new comment"""
    try:
        post = await Post.objects.aget(post_id=data.post)
        user = await Account.objects.aget(id=data.user_id)
        
        comment = await Comment.objects.acreate(
            post=post,
            user=user,
            comment_text=data.comment_text
        )
        
        like_count = await sync_to_async(lambda: comment.like_count)()
        
        return {
            "comment_id": comment.comment_id,
            "post": comment.post.post_id,
            "user": {
                "id": comment.user.id,
                "username": comment.user.username,
                "email": comment.user.email,
            },
            "comment_datetime": comment.comment_datetime.isoformat(),
            "comment_text": comment.comment_text,
            "like_count": like_count,
        }
    except Post.DoesNotExist:
        return JSON({"error": "Post not found"}, status_code=404)
    except Account.DoesNotExist:
        return JSON({"error": "User not found"}, status_code=404)

class UpdateCommentSerializer(Serializer):
    comment_text: str

@api.put("/comments/{comment_id}")
async def update_comment(comment_id: int, data: UpdateCommentSerializer):
    """Update a comment"""
    try:
        comment = await Comment.objects.aget(comment_id=comment_id)
        comment.comment_text = data.comment_text
        await sync_to_async(comment.save)()
        
        like_count = await sync_to_async(lambda: comment.like_count)()
        
        return {
            "comment_id": comment.comment_id,
            "post": comment.post.post_id,
            "user": {
                "id": comment.user.id,
                "username": comment.user.username,
                "email": comment.user.email,
            },
            "comment_datetime": comment.comment_datetime.isoformat(),
            "comment_text": comment.comment_text,
            "like_count": like_count,
        }
    except Comment.DoesNotExist:
        return JSON({"error": "Comment not found"}, status_code=404)

@api.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int):
    """Delete a comment"""
    try:
        comment = await Comment.objects.aget(comment_id=comment_id)
        await sync_to_async(comment.delete)()
        return {"message": "Comment deleted successfully"}
    except Comment.DoesNotExist:
        return JSON({"error": "Comment not found"}, status_code=404)

# Likes endpoints
class LikePostSerializer(Serializer):
    post: int
    user_id: int

@api.post("/postlikes")
async def like_post(data: LikePostSerializer):
    """Like a post"""
    try:
        post = await Post.objects.aget(post_id=data.post)
        user = await Account.objects.aget(id=data.user_id)
        
        def create_like():
            post_like, created = PostLike.objects.get_or_create(post=post, user=user)
            return created
        
        created = await sync_to_async(create_like)()
        like_count = await sync_to_async(lambda: post.like_count)()
        
        return {
            "liked": created,
            "like_count": like_count
        }
    except Post.DoesNotExist:
        return JSON({"error": "Post not found"}, status_code=404)
    except Account.DoesNotExist:
        return JSON({"error": "User not found"}, status_code=404)

@api.delete("/postlikes/{post_id}/{user_id}")
async def unlike_post(post_id: int, user_id: int):
    """Unlike a post"""
    try:
        def delete_like():
            post_like = PostLike.objects.get(post_id=post_id, user_id=user_id)
            post_like.delete()
        
        await sync_to_async(delete_like)()
        
        post = await Post.objects.aget(post_id=post_id)
        like_count = await sync_to_async(lambda: post.like_count)()
        
        return {
            "message": "Post unliked successfully",
            "like_count": like_count
        }
    except PostLike.DoesNotExist:
        return JSON({"error": "Like not found"}, status_code=404)
    except Post.DoesNotExist:
        return JSON({"error": "Post not found"}, status_code=404)

class LikeCommentSerializer(Serializer):
    comment: int
    user_id: int

@api.post("/commentlikes")
async def like_comment(data: LikeCommentSerializer):
    """Like a comment"""
    try:
        comment = await Comment.objects.aget(comment_id=data.comment)
        user = await Account.objects.aget(id=data.user_id)
        
        def create_like():
            comment_like, created = CommentLike.objects.get_or_create(comment=comment, user=user)
            return created
        
        created = await sync_to_async(create_like)()
        like_count = await sync_to_async(lambda: comment.like_count)()
        
        return {
            "liked": created,
            "like_count": like_count
        }
    except Comment.DoesNotExist:
        return JSON({"error": "Comment not found"}, status_code=404)
    except Account.DoesNotExist:
        return JSON({"error": "User not found"}, status_code=404)

@api.delete("/commentlikes/{comment_id}/{user_id}")
async def unlike_comment(comment_id: int, user_id: int):
    """Unlike a comment"""
    try:
        def delete_like():
            comment_like = CommentLike.objects.get(comment_id=comment_id, user_id=user_id)
            comment_like.delete()
        
        await sync_to_async(delete_like)()
        
        comment = await Comment.objects.aget(comment_id=comment_id)
        like_count = await sync_to_async(lambda: comment.like_count)()
        
        return {
            "message": "Comment unliked successfully",
            "like_count": like_count
        }
    except CommentLike.DoesNotExist:
        return JSON({"error": "Like not found"}, status_code=404)
    except Comment.DoesNotExist:
        return JSON({"error": "Comment not found"}, status_code=404)

