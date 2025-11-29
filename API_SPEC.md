# API Specification - Olaf Backend

## Base URLs
- **Development**: `http://127.0.0.1:8000/api/`
- **Production**: `https://olaf-backend.onrender.com/api/`

## Authentication

ระบบใช้ JWT Authentication โดย token จะถูกเก็บใน HTTP-only cookies และสามารถส่งผ่าน Authorization header ได้

### Headers สำหรับ Authenticated Requests
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
Content-Type: application/json
```

### Cookie Settings
- `access`: Access token (HttpOnly, expires in 1 hour)
- `refresh`: Refresh token (HttpOnly, expires in 7 days)
- `csrftoken`: CSRF token

---

## 1. Authentication Endpoints

### 1.1 Get CSRF Token
```http
GET /api/auth/csrf/
```

**Headers:**
```
None required
```

**Response (200 OK):**
```json
{
    "message": "CSRF token available",
    "csrfToken": "csrf_token_value"
}
```

**Response Headers:**
```
X-CSRFToken: <csrf_token_value>
Set-Cookie: csrftoken=<csrf_token_value>; Path=/
```

---

### 1.2 User Registration
```http
POST /api/auth/register/
```

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "0812345678",
    "password": "secure_password123",
    "password2": "secure_password123"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully!",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "0812345678",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

**Response Headers:**
```
Set-Cookie: access=<access_token>; HttpOnly; Path=/; Max-Age=3600
Set-Cookie: refresh=<refresh_token>; HttpOnly; Path=/; Max-Age=604800
X-CSRFToken: <csrf_token>
```

**Error Responses:**
- `400 Bad Request`: Validation error
- `500 Internal Server Error`: Server error

---

### 1.3 User Login
```http
POST /api/auth/login/
```

**Headers:**
```
Content-Type: application/json
X-CSRFToken: <csrf_token> (optional but recommended)
```

**Request Body:**
```json
{
    "email": "john@example.com",
    "password": "secure_password123"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "0812345678",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

**Response Headers:**
```
Set-Cookie: access=<access_token>; HttpOnly; Path=/; Max-Age=3600
Set-Cookie: refresh=<refresh_token>; HttpOnly; Path=/; Max-Age=604800
X-CSRFToken: <csrf_token>
```

**Error Responses:**
- `401 Unauthorized`: Invalid email or password
- `400 Bad Request`: Validation error

---

### 1.4 Refresh Token
```http
POST /api/auth/refresh-token/
```

**Headers:**
```
Content-Type: application/json
```

**Request Body (Optional - สามารถส่ง refresh token ผ่าน):**
```json
{
    "refresh": "refresh_token_here"  // Optional: ถ้าไม่ส่งจะใช้จาก cookie
}
```

**หรือส่งผ่าน Authorization Header:**
```
Authorization: Bearer <refresh_token>
```

**Response (200 OK):**
```json
{
    "access": "new_access_token"
}
```

**Response Headers:**
```
Set-Cookie: access=<new_access_token>; HttpOnly; Path=/; Max-Age=3600
Set-Cookie: refresh=<new_refresh_token>; HttpOnly; Path=/; Max-Age=604800 (if rotated)
X-CSRFToken: <csrf_token>
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token

---

### 1.5 Get Current User
```http
GET /api/auth/user/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "0812345678",
    "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated

---

### 1.6 Check Authentication
```http
GET /api/auth/check/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "isAuthenticated": true,
    "user_id": 1
}
```

**Error Responses:**
- `401 Unauthorized`: Not authenticated

---

### 1.7 Logout
```http
POST /api/auth/logout/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{}
```

**Response (200 OK):**
```json
{
    "message": "Logged out successfully"
}
```

**Response Headers:**
```
Set-Cookie: access=; expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/
Set-Cookie: refresh=; expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/
```

---

## 2. Blog Posts Endpoints

### 2.1 List Posts
```http
GET /api/posts/
```

**Headers:**
```
Authorization: Bearer <access_token> (optional)
```

**Query Parameters:**
- `page`: Page number (pagination)
- `page_size`: Items per page

**Response (200 OK):**
```json
[
    {
        "post_id": 1,
        "header": "Post Title",
        "short": "Short description",
        "post_text": "Full post content",
        "post_datetime": "2024-01-15T10:30:00Z",
        "user": {
            "id": 1,
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com"
        },
        "user_id": 1,
        "image": "old_image_url",
        "image_url": "primary_image_url",
        "image_secure_url": "https://res.cloudinary.com/...",
        "like_count": 5,
        "comment_count": 3,
        "liked": false,
        "images": [
            {
                "id": 1,
                "image": "https://res.cloudinary.com/...",
                "caption": "Image caption",
                "is_primary": true,
                "sort_order": 0
            }
        ],
        "primary_image": {
            "id": 1,
            "image": "https://res.cloudinary.com/...",
            "caption": "Image caption",
            "is_primary": true
        },
        "primary_image_url": "https://res.cloudinary.com/...",
        "image_count": 1,
        "comments": [
            {
                "comment_id": 1,
                "comment_text": "Great post!",
                "comment_datetime": "2024-01-15T11:00:00Z",
                "user": {
                    "id": 2,
                    "username": "jane_doe"
                },
                "like_count": 2
            }
        ]
    }
]
```

---

### 2.2 Get Post Detail
```http
GET /api/posts/{post_id}/
```

**Headers:**
```
Authorization: Bearer <access_token> (optional)
```

**Response (200 OK):**
```json
{
    "post_id": 1,
    "header": "Post Title",
    "short": "Short description",
    "post_text": "Full post content",
    "post_datetime": "2024-01-15T10:30:00Z",
    "user": {...},
    "like_count": 5,
    "comment_count": 3,
    "liked": false,
    "images": [...],
    "primary_image": {...},
    "comments": [...]
}
```

**Error Responses:**
- `404 Not Found`: Post not found

---

### 2.3 Create Post
```http
POST /api/posts/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "header": "Post Title",
    "short": "Short description",
    "post_text": "Full post content",
    "user_id": 1
}
```

**Response (201 Created):**
```json
{
    "post_id": 1,
    "header": "Post Title",
    "short": "Short description",
    "post_text": "Full post content",
    "post_datetime": "2024-01-15T10:30:00Z",
    "user": {...},
    "like_count": 0,
    "comment_count": 0,
    "liked": false
}
```

**Error Responses:**
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Not authenticated

---

### 2.4 Create Post with Image (Frontend Upload)
```http
POST /api/posts/create-with-image/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "header": "Post Title",
    "short": "Short description",
    "post_text": "Full post content",
    "image_url": "https://res.cloudinary.com/dm02oprw0/image/upload/v1764353463/olaf/blog/v0v2kfys1k7yqtf5oghn.jpg",
    "caption": "Image caption",
    "is_primary": true,
    "sort_order": 0
}
```

**Response (201 Created):**
```json
{
    "post_id": 1,
    "header": "Post Title",
    "post_text": "Full post content",
    "images": [
        {
            "id": 1,
            "image": "https://res.cloudinary.com/...",
            "caption": "Image caption",
            "is_primary": true,
            "sort_order": 0
        }
    ],
    "primary_image": {...},
    "primary_image_url": "https://res.cloudinary.com/..."
}
```

**Note:** `user_id` จะถูกใช้จาก authenticated user อัตโนมัติ

---

### 2.5 Update Post
```http
PUT /api/posts/{post_id}/
PATCH /api/posts/{post_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "header": "Updated Title",
    "post_text": "Updated content"
}
```

**Response (200 OK):**
```json
{
    "post_id": 1,
    "header": "Updated Title",
    "post_text": "Updated content",
    ...
}
```

**Error Responses:**
- `403 Forbidden`: Not the post owner
- `404 Not Found`: Post not found

---

### 2.6 Delete Post
```http
DELETE /api/posts/{post_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (204 No Content)**

**Error Responses:**
- `403 Forbidden`: Not the post owner
- `404 Not Found`: Post not found

---

## 3. Post Images Endpoints

### 3.1 Upload Image to Post
```http
POST /api/posts/{post_id}/upload-image/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
X-CSRFToken: <csrf_token>
```

**Request Body (Form Data):**
```
image: <file>
caption: "Image caption" (optional)
is_primary: true (optional, default: false)
sort_order: 0 (optional, default: 0)
```

**Response (201 Created):**
```json
{
    "id": 1,
    "image": "https://res.cloudinary.com/...",
    "caption": "Image caption",
    "image_url": "http://res.cloudinary.com/...",
    "image_secure_url": "https://res.cloudinary.com/...",
    "image_public_id": "shared/images/abc123",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "is_primary": true,
    "sort_order": 0
}
```

---

### 3.2 Add Image Path to Post (Frontend Upload)
```http
POST /api/posts/{post_id}/add-image-path/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "image": "https://res.cloudinary.com/dm02oprw0/image/upload/v1764353463/olaf/blog/v0v2kfys1k7yqtf5oghn.jpg",
    "caption": "Image caption",
    "is_primary": true,
    "sort_order": 0
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "image": "https://res.cloudinary.com/...",
    "caption": "Image caption",
    "is_primary": true,
    "sort_order": 0
}
```

---

### 3.3 Get All Images for Post
```http
GET /api/posts/{post_id}/images/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "image": "https://res.cloudinary.com/...",
        "caption": "Image caption",
        "is_primary": true,
        "sort_order": 0
    },
    {
        "id": 2,
        "image": "https://res.cloudinary.com/...",
        "caption": "Second image",
        "is_primary": false,
        "sort_order": 1
    }
]
```

---

### 3.4 Get Primary Image for Post
```http
GET /api/posts/{post_id}/primary-image/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "image": "https://res.cloudinary.com/...",
    "caption": "Image caption",
    "is_primary": true,
    "sort_order": 0
}
```

**Response (404 Not Found):**
```json
{
    "detail": "No primary image found"
}
```

---

### 3.5 Set Primary Image
```http
PATCH /api/images/{image_id}/set-primary/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "image": "https://res.cloudinary.com/...",
    "is_primary": true,
    "message": "Primary image updated"
}
```

---

### 3.6 Delete Image
```http
DELETE /api/images/{image_id}/delete/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (204 No Content)**

**Error Responses:**
- `404 Not Found`: Image not found
- `403 Forbidden`: Not authorized

---

## 4. Comments Endpoints

### 4.1 List Comments
```http
GET /api/comments/
```

**Query Parameters:**
- `post`: Filter by post_id

**Response (200 OK):**
```json
[
    {
        "comment_id": 1,
        "post": 1,
        "user": {
            "id": 2,
            "username": "jane_doe",
            "first_name": "Jane",
            "last_name": "Doe"
        },
        "comment_text": "Great post!",
        "comment_datetime": "2024-01-15T11:00:00Z",
        "like_count": 2
    }
]
```

---

### 4.2 Get Comment Detail
```http
GET /api/comments/{comment_id}/
```

**Response (200 OK):**
```json
{
    "comment_id": 1,
    "post": 1,
    "user": {...},
    "comment_text": "Great post!",
    "comment_datetime": "2024-01-15T11:00:00Z",
    "like_count": 2
}
```

---

### 4.3 Create Comment
```http
POST /api/comments/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "post": 1,
    "user_id": 2,
    "comment_text": "Great post!"
}
```

**Response (201 Created):**
```json
{
    "comment_id": 1,
    "post": 1,
    "user": {...},
    "comment_text": "Great post!",
    "comment_datetime": "2024-01-15T11:00:00Z",
    "like_count": 0
}
```

---

### 4.4 Update Comment
```http
PUT /api/comments/{comment_id}/
PATCH /api/comments/{comment_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "comment_text": "Updated comment"
}
```

**Response (200 OK):**
```json
{
    "comment_id": 1,
    "comment_text": "Updated comment",
    ...
}
```

---

### 4.5 Delete Comment
```http
DELETE /api/comments/{comment_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (204 No Content)**

---

## 5. Post Likes Endpoints

### 5.1 Like/Unlike Post
```http
POST /api/postlikes/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "post": 1,
    "user": 2
}
```

**Response (201 Created - New Like):**
```json
{
    "liked": true,
    "like_count": 6
}
```

**Response (200 OK - Already Liked):**
```json
{
    "liked": false,
    "like_count": 5
}
```

---

### 5.2 Unlike Post
```http
DELETE /api/postlikes/{post_id}/{user_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (204 No Content)**

**Error Responses:**
- `404 Not Found`: Like not found

---

## 6. Comment Likes Endpoints

### 6.1 Like/Unlike Comment
```http
POST /api/commentlikes/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "comment": 1,
    "user": 2
}
```

**Response (201 Created - New Like):**
```json
{
    "liked": true,
    "like_count": 3
}
```

**Response (200 OK - Already Liked):**
```json
{
    "liked": false,
    "like_count": 2
}
```

---

### 6.2 Unlike Comment
```http
DELETE /api/commentlikes/{comment_id}/{user_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (204 No Content)**

---

## 7. CloudDiary Endpoints

### 7.1 List CloudDiary Entries
```http
GET /api/clouddiary/
```

**Query Parameters:**
- `is_public`: Filter by public status (true/false)
- `author`: Filter by author_id

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "title": "Diary Title",
        "content": "Diary content",
        "author": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com"
        },
        "author_id": 1,
        "is_public": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "images": [...],
        "image_count": 2,
        "shared_images": [...],
        "primary_image": {...},
        "primary_image_url": "https://res.cloudinary.com/...",
        "shared_image_count": 3
    }
]
```

---

### 7.2 Get CloudDiary Detail
```http
GET /api/clouddiary/{id}/
```

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "Diary Title",
    "content": "Diary content",
    "author": {...},
    "is_public": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "shared_images": [...],
    "primary_image": {...}
}
```

---

### 7.3 Create CloudDiary Entry
```http
POST /api/clouddiary/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "title": "Diary Title",
    "content": "Diary content",
    "author_id": 1,
    "is_public": true
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "title": "Diary Title",
    "content": "Diary content",
    "author": {...},
    "is_public": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### 7.4 Update CloudDiary Entry
```http
PUT /api/clouddiary/{id}/
PATCH /api/clouddiary/{id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "title": "Updated Title",
    "content": "Updated content",
    "is_public": false
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "Updated Title",
    "content": "Updated content",
    ...
}
```

---

### 7.5 Delete CloudDiary Entry
```http
DELETE /api/clouddiary/{id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (204 No Content)**

---

### 7.6 Get User's CloudDiary Entries
```http
GET /api/clouddiary/my-diaries/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "title": "My Diary",
        "content": "Content",
        "is_public": true,
        ...
    }
]
```

---

## 8. CloudDiary Images Endpoints

### 8.1 Upload Shared Image to CloudDiary
```http
POST /api/clouddiary/{clouddiary_id}/upload-shared-image/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
X-CSRFToken: <csrf_token>
```

**Request Body (Form Data):**
```
image: <file>
caption: "Image caption" (optional)
is_primary: true (optional)
sort_order: 0 (optional)
```

**Response (201 Created):**
```json
{
    "id": 1,
    "image": "https://res.cloudinary.com/...",
    "caption": "Image caption",
    "is_primary": true,
    "sort_order": 0
}
```

---

### 8.2 Add Image Path to CloudDiary (Frontend Upload)
```http
POST /api/clouddiary/{clouddiary_id}/add-image-path/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "image": "https://res.cloudinary.com/dm02oprw0/image/upload/v1764353463/olaf/clouddiary/abc123.jpg",
    "caption": "Image caption",
    "is_primary": true,
    "sort_order": 0
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "image": "https://res.cloudinary.com/...",
    "caption": "Image caption",
    "is_primary": true
}
```

---

### 8.3 Get All Shared Images for CloudDiary
```http
GET /api/clouddiary/{clouddiary_id}/shared-images/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "image": "https://res.cloudinary.com/...",
        "caption": "Image caption",
        "is_primary": true,
        "sort_order": 0
    }
]
```

---

### 8.4 Get Primary Shared Image for CloudDiary
```http
GET /api/clouddiary/{clouddiary_id}/primary-shared-image/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "image": "https://res.cloudinary.com/...",
    "caption": "Image caption",
    "is_primary": true
}
```

---

### 8.5 Set Primary Shared Image
```http
PATCH /api/clouddiary/shared-images/{image_id}/set-primary/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "is_primary": true,
    "message": "Primary image updated"
}
```

---

### 8.6 Delete Shared Image
```http
DELETE /api/clouddiary/shared-images/{image_id}/delete/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (204 No Content)**

---

## 9. Shared Images Generic Endpoints

### 9.1 Upload Image to Any Object
```http
POST /api/shared-images/upload/{content_type_id}/{object_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
X-CSRFToken: <csrf_token>
```

**Request Body (Form Data):**
```
image: <file>
caption: "Image caption" (optional)
is_primary: true (optional)
sort_order: 0 (optional)
```

**Response (201 Created):**
```json
{
    "id": 1,
    "image": "https://res.cloudinary.com/...",
    "caption": "Image caption",
    "is_primary": true,
    "sort_order": 0
}
```

---

### 9.2 Add Image Path to Any Object
```http
POST /api/shared-images/add-path/{content_type_id}/{object_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{
    "image": "https://res.cloudinary.com/...",
    "caption": "Image caption",
    "is_primary": true,
    "sort_order": 0
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "image": "https://res.cloudinary.com/...",
    "caption": "Image caption",
    "is_primary": true
}
```

---

### 9.3 Get Images for Any Object
```http
GET /api/shared-images/objects/{content_type_id}/{object_id}/list/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "image": "https://res.cloudinary.com/...",
        "caption": "Image caption",
        "is_primary": true,
        "sort_order": 0
    }
]
```

---

### 9.4 Get Primary Image for Any Object
```http
GET /api/shared-images/objects/{content_type_id}/{object_id}/primary/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "image": "https://res.cloudinary.com/...",
    "caption": "Image caption",
    "is_primary": true
}
```

---

### 9.5 Set Primary Image
```http
PATCH /api/shared-images/images/{image_id}/set-primary/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "is_primary": true,
    "message": "Primary image updated"
}
```

---

### 9.6 Delete Image
```http
DELETE /api/shared-images/images/{image_id}/delete/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (204 No Content)**

---

## Error Responses

### Standard Error Format
```json
{
    "error": "Error message",
    "details": {
        "field_name": ["Error message for this field"]
    }
}
```

### HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid
- `403 Forbidden`: Not authorized to perform action
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Notes

1. **Authentication**: 
   - Token สามารถส่งผ่าน Cookie (อัตโนมัติ) หรือ Authorization header
   - Refresh token สามารถส่งผ่าน Cookie, Request Body, หรือ Authorization header

2. **CORS**: 
   - Frontend ต้องใช้ `credentials: 'include'` ในทุก request
   - CORS allowed origins: `http://localhost:3000`, `https://olafs.netlify.app`

3. **Image Upload**:
   - รองรับ 2 วิธี: Upload ผ่าน backend หรือ Upload ไป Cloudinary โดยตรงแล้วส่ง URL กลับมา
   - Cloudinary folder structure: `olaf/blog/` สำหรับ posts, `olaf/clouddiary/` สำหรับ clouddiary

4. **Pagination**: 
   - ใช้ Django REST Framework pagination
   - Query parameters: `page`, `page_size`

5. **Permissions**:
   - Public endpoints: List posts, Get post detail, List comments
   - Authenticated endpoints: Create/Update/Delete posts, Create comments, Like/Unlike

---

## Example Frontend Implementation

```javascript
// Base API configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Helper function for authenticated requests
async function apiRequest(endpoint, options = {}) {
    const token = getAccessToken(); // Get from cookie or storage
    
    const config = {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        },
        credentials: 'include'
    };
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (response.status === 401) {
        // Try to refresh token
        const refreshed = await refreshToken();
        if (refreshed) {
            // Retry request
            return apiRequest(endpoint, options);
        }
        // Redirect to login
        window.location.href = '/login';
    }
    
    return response.json();
}

// Example: Create post with image
async function createPostWithImage(postData, imageUrl) {
    return apiRequest('/posts/create-with-image/', {
        method: 'POST',
        body: JSON.stringify({
            ...postData,
            image_url: imageUrl,
            is_primary: true
        })
    });
}
```

---

**Last Updated**: 2024-01-15
**Version**: 1.0.0

