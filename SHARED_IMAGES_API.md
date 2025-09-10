# Shared Images API Documentation

## Overview
ระบบ Shared Images เป็นระบบจัดการรูปภาพแบบรวมศูนย์ที่สามารถใช้ร่วมกันระหว่าง Blog Posts และ CloudDiary entries โดยใช้ Cloudinary เป็น storage backend

## Features
- รองรับการอัปโหลดรูปภาพหลายรูปต่อ object
- ระบบ Primary Image (รูปภาพหลัก)
- การเรียงลำดับรูปภาพ (Sort Order)
- Caption สำหรับแต่ละรูปภาพ
- Generic Foreign Key สำหรับเชื่อมต่อกับ model ใดก็ได้

## API Endpoints

### 1. Blog Posts Image Management

#### Upload Image to Post
```
POST /api/posts/{post_id}/upload-image/
```
**Request Body:**
```json
{
    "image": "file",
    "caption": "Optional caption",
    "is_primary": false,
    "sort_order": 0
}
```

#### Get All Images for Post
```
GET /api/posts/{post_id}/images/
```

#### Get Primary Image for Post
```
GET /api/posts/{post_id}/primary-image/
```

#### Set Primary Image
```
PATCH /api/images/{image_id}/set-primary/
```

#### Delete Image
```
DELETE /api/images/{image_id}/delete/
```

### 2. CloudDiary Image Management

#### Upload Image to CloudDiary
```
POST /api/clouddiary/{clouddiary_id}/upload-shared-image/
```
**Request Body:**
```json
{
    "image": "file",
    "caption": "Optional caption",
    "is_primary": false,
    "sort_order": 0
}
```

#### Get All Shared Images for CloudDiary
```
GET /api/clouddiary/{clouddiary_id}/shared-images/
```

#### Get Primary Shared Image for CloudDiary
```
GET /api/clouddiary/{clouddiary_id}/primary-shared-image/
```

#### Set Primary Image
```
PATCH /api/clouddiary/shared-images/{image_id}/set-primary/
```

#### Delete Shared Image
```
DELETE /api/clouddiary/shared-images/{image_id}/delete/
```

### 3. Generic Shared Images API

#### Upload Image to Any Object
```
POST /api/shared-images/upload/{content_type_id}/{object_id}/
```

#### Get Images for Any Object
```
GET /api/shared-images/objects/{content_type_id}/{object_id}/list/
```

#### Get Primary Image for Any Object
```
GET /api/shared-images/objects/{content_type_id}/{object_id}/primary/
```

## Response Format

### Image Object
```json
{
    "id": 1,
    "image": "cloudinary_url",
    "caption": "Image caption",
    "image_url": "http://res.cloudinary.com/...",
    "image_public_id": "shared/images/abc123",
    "image_secure_url": "https://res.cloudinary.com/...",
    "uploaded_at": "2024-01-01T00:00:00Z",
    "is_primary": true,
    "sort_order": 0
}
```

### Post with Images
```json
{
    "post_id": 1,
    "header": "Post Title",
    "post_text": "Post content",
    "user": {...},
    "image": "old_image_url",  // Backward compatibility
    "image_url": "primary_image_url",
    "images": [...],  // All shared images
    "primary_image": {...},  // Primary image object
    "primary_image_url": "primary_image_url",
    "image_count": 3,
    "like_count": 5,
    "comment_count": 2,
    "comments": [...],
    "liked": false
}
```

### CloudDiary with Images
```json
{
    "id": 1,
    "title": "Diary Title",
    "content": "Diary content",
    "author": {...},
    "images": [...],  // Old images (backward compatibility)
    "image_count": 2,
    "shared_images": [...],  // New shared images
    "primary_image": {...},  // Primary shared image
    "primary_image_url": "primary_image_url",
    "shared_image_count": 3,
    "is_public": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

## Usage Examples

### 1. Create Post with Images
```bash
# 1. Create post
POST /api/posts/
{
    "header": "My Blog Post",
    "post_text": "This is my blog post content",
    "user_id": 1
}

# 2. Upload images
POST /api/posts/1/upload-image/
{
    "image": "file1.jpg",
    "caption": "Main image",
    "is_primary": true,
    "sort_order": 0
}

POST /api/posts/1/upload-image/
{
    "image": "file2.jpg",
    "caption": "Secondary image",
    "is_primary": false,
    "sort_order": 1
}
```

### 2. Create CloudDiary with Images
```bash
# 1. Create clouddiary
POST /api/clouddiary/
{
    "title": "My Diary Entry",
    "content": "This is my diary content",
    "author_id": 1,
    "is_public": true
}

# 2. Upload images
POST /api/clouddiary/1/upload-shared-image/
{
    "image": "diary_image.jpg",
    "caption": "Diary photo",
    "is_primary": true,
    "sort_order": 0
}
```

### 3. Change Primary Image
```bash
# Set different image as primary
PATCH /api/images/2/set-primary/
```

## Authentication
All endpoints require authentication using the CustomAuthentication system.

## Error Handling
- 400: Bad Request (invalid data)
- 401: Unauthorized (not authenticated)
- 403: Forbidden (no permission)
- 404: Not Found (object/image not found)
- 500: Internal Server Error

## Notes
- ระบบรองรับ backward compatibility กับ image fields เดิม
- รูปภาพจะถูกเก็บใน Cloudinary folder: `shared/images/`
- Primary image จะมีได้เพียง 1 รูปต่อ object
- การลบ primary image จะไม่ทำให้ primary status ถูกโอนไปยังรูปอื่นอัตโนมัติ
