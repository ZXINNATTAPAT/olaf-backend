"""
Django-Bolt API routes for CloudDiary endpoints.
"""
from django_bolt import BoltAPI
from django_bolt.serializers import Serializer, Nested
from django_bolt.responses import JSON, Response
from typing import Annotated, Optional
from msgspec import Meta
from asgiref.sync import sync_to_async
from .models import CloudDiary, CloudDiaryImage
from authentication.models import Account
from shared_images.serializers import SharedImageSerializer
from django.db.models import Q

# Initialize Bolt API with OpenAPI/Swagger configuration
from django_bolt import OpenAPIConfig

api = BoltAPI(
    openapi_config=OpenAPIConfig(
        title="Olaf Backend API - CloudDiary",
        version="1.0.0",
        description="CloudDiary endpoints for Olaf platform",
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

class CloudDiarySerializer(Serializer):
    id: int
    title: str
    content: Optional[str] = None
    author: Annotated[UserSerializer, Nested(UserSerializer)]
    created_at: str
    updated_at: str
    is_public: bool
    primary_image_url: Optional[str] = None
    image_count: int

class CreateCloudDiarySerializer(Serializer):
    title: Annotated[str, Meta(min_length=1, max_length=200)]
    content: Optional[str] = None
    is_public: bool = True
    author_id: int

class UpdateCloudDiarySerializer(Serializer):
    title: Optional[Annotated[str, Meta(min_length=1, max_length=200)]] = None
    content: Optional[str] = None
    is_public: Optional[bool] = None

# API Routes
@api.get("/")
async def list_clouddiaries(page: int = 1, page_size: int = 20, user_id: Optional[int] = None):
    """List cloud diaries - public or user's own"""
    offset = (page - 1) * page_size
    
    # Build queryset
    queryset = CloudDiary.objects.select_related('author').prefetch_related('images', 'shared_images')
    
    # Filter: public diaries or user's own diaries
    if user_id:
        queryset = queryset.filter(Q(is_public=True) | Q(author_id=user_id))
    else:
        queryset = queryset.filter(is_public=True)
    
    queryset = queryset.order_by('-created_at')[offset:offset + page_size]
    
    results = []
    async for diary in queryset:
        image_count = await sync_to_async(lambda: diary.image_count)()
        results.append({
            "id": diary.id,
            "title": diary.title,
            "content": diary.content,
            "author": {
                "id": diary.author.id,
                "username": diary.author.username,
                "email": diary.author.email,
            },
            "created_at": diary.created_at.isoformat(),
            "updated_at": diary.updated_at.isoformat(),
            "is_public": diary.is_public,
            "primary_image_url": diary.primary_image_url,
            "image_count": image_count,
        })
    
    total_count = await sync_to_async(lambda: CloudDiary.objects.filter(
        Q(is_public=True) | Q(author_id=user_id) if user_id else Q(is_public=True)
    ).count())()
    
    return {
        "count": total_count,
        "next": f"/api/clouddiary?page={page + 1}" if len(results) == page_size else None,
        "previous": f"/api/clouddiary?page={page - 1}" if page > 1 else None,
        "results": results
    }

@api.get("/{diary_id}")
async def get_clouddiary(diary_id: int):
    """Get a single cloud diary by ID"""
    try:
        diary = await CloudDiary.objects.select_related('author').prefetch_related('images', 'shared_images').aget(id=diary_id)
        
        # Check if diary is public or user's own (TODO: add user authentication)
        if not diary.is_public:
            # TODO: Check if current user is the author
            pass
        
        image_count = await sync_to_async(lambda: diary.image_count)()
        
        return {
            "id": diary.id,
            "title": diary.title,
            "content": diary.content,
            "author": {
                "id": diary.author.id,
                "username": diary.author.username,
                "email": diary.author.email,
            },
            "created_at": diary.created_at.isoformat(),
            "updated_at": diary.updated_at.isoformat(),
            "is_public": diary.is_public,
            "primary_image_url": diary.primary_image_url,
            "image_count": image_count,
        }
    except CloudDiary.DoesNotExist:
        return JSON({"error": "Cloud diary not found"}, status_code=404)

@api.post("/")
async def create_clouddiary(data: CreateCloudDiarySerializer):
    """Create a new cloud diary"""
    try:
        author = await Account.objects.aget(id=data.author_id)
        
        diary = await CloudDiary.objects.acreate(
            title=data.title,
            content=data.content,
            author=author,
            is_public=data.is_public
        )
        
        image_count = await sync_to_async(lambda: diary.image_count)()
        
        return {
            "id": diary.id,
            "title": diary.title,
            "content": diary.content,
            "author": {
                "id": diary.author.id,
                "username": diary.author.username,
                "email": diary.author.email,
            },
            "created_at": diary.created_at.isoformat(),
            "updated_at": diary.updated_at.isoformat(),
            "is_public": diary.is_public,
            "primary_image_url": diary.primary_image_url,
            "image_count": image_count,
        }
    except Account.DoesNotExist:
        return JSON({"error": "User not found"}, status_code=404)

@api.put("/{diary_id}")
async def update_clouddiary(diary_id: int, data: UpdateCloudDiarySerializer):
    """Update a cloud diary"""
    try:
        diary = await CloudDiary.objects.aget(id=diary_id)
        
        # TODO: Check if current user is the author
        
        if data.title is not None:
            diary.title = data.title
        if data.content is not None:
            diary.content = data.content
        if data.is_public is not None:
            diary.is_public = data.is_public
        
        await sync_to_async(diary.save)()
        
        # Reload with relations
        diary = await CloudDiary.objects.select_related('author').prefetch_related('images', 'shared_images').aget(id=diary_id)
        image_count = await sync_to_async(lambda: diary.image_count)()
        
        return {
            "id": diary.id,
            "title": diary.title,
            "content": diary.content,
            "author": {
                "id": diary.author.id,
                "username": diary.author.username,
                "email": diary.author.email,
            },
            "created_at": diary.created_at.isoformat(),
            "updated_at": diary.updated_at.isoformat(),
            "is_public": diary.is_public,
            "primary_image_url": diary.primary_image_url,
            "image_count": image_count,
        }
    except CloudDiary.DoesNotExist:
        return JSON({"error": "Cloud diary not found"}, status_code=404)

@api.delete("/{diary_id}")
async def delete_clouddiary(diary_id: int):
    """Delete a cloud diary"""
    try:
        diary = await CloudDiary.objects.aget(id=diary_id)
        
        # TODO: Check if current user is the author
        
        await sync_to_async(diary.delete)()
        return {"message": "Cloud diary deleted successfully"}
    except CloudDiary.DoesNotExist:
        return JSON({"error": "Cloud diary not found"}, status_code=404)

@api.get("/my-diaries")
async def get_my_clouddiaries(user_id: int, page: int = 1, page_size: int = 20):
    """Get current user's cloud diaries"""
    offset = (page - 1) * page_size
    
    diaries = CloudDiary.objects.filter(author_id=user_id).select_related('author').prefetch_related('images', 'shared_images').order_by('-created_at')[offset:offset + page_size]
    
    results = []
    async for diary in diaries:
        image_count = await sync_to_async(lambda: diary.image_count)()
        results.append({
            "id": diary.id,
            "title": diary.title,
            "content": diary.content,
            "author": {
                "id": diary.author.id,
                "username": diary.author.username,
                "email": diary.author.email,
            },
            "created_at": diary.created_at.isoformat(),
            "updated_at": diary.updated_at.isoformat(),
            "is_public": diary.is_public,
            "primary_image_url": diary.primary_image_url,
            "image_count": image_count,
        })
    
    total_count = await sync_to_async(lambda: CloudDiary.objects.filter(author_id=user_id).count())()
    
    return {
        "count": total_count,
        "next": f"/api/clouddiary/my-diaries?page={page + 1}" if len(results) == page_size else None,
        "previous": f"/api/clouddiary/my-diaries?page={page - 1}" if page > 1 else None,
        "results": results
    }

