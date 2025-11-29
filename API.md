# API Documentation

Complete API reference for Olaf Backend.

## Base URLs

- **Development**: `http://localhost:8000/api/`
- **Production**: `https://web-production-ba20a.up.railway.app/api/`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Tokens are stored in HTTP-only cookies.

### Headers for Authenticated Requests
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

## Authentication Endpoints

### Get CSRF Token
```http
GET /api/auth/csrf/
```

**Response (200 OK):**
```json
{
    "message": "CSRF token available",
    "csrfToken": "csrf_token_value"
}
```

---

### User Registration
```http
POST /api/auth/register
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

---

### User Login
```http
POST /api/auth/login
Content-Type: application/json
X-CSRFToken: <csrf_token>
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
        "email": "john@example.com"
    }
}
```

**Response Headers:**
```
Set-Cookie: access=<access_token>; HttpOnly; Path=/; Max-Age=3600
Set-Cookie: refresh=<refresh_token>; HttpOnly; Path=/; Max-Age=604800
X-CSRFToken: <csrf_token>
```

---

### Get Current User
```http
GET /api/auth/user
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
    "last_name": "Doe"
}
```

---

### Check Authentication
```http
GET /api/auth/check
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "authenticated": true,
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    }
}
```

---

### Refresh Token
```http
POST /api/auth/refresh-token
Content-Type: application/json
```

**Request Body:** (empty or refresh token in cookie)

**Response (200 OK):**
```json
{
    "access": "new_access_token",
    "refresh": "new_refresh_token",
    "message": "Token refreshed successfully"
}
```

---

### Logout
```http
POST /api/auth/logout
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (200 OK):**
```json
{
    "message": "Logged out successfully"
}
```

---

## Blog Endpoints

### List Posts
```http
GET /api/posts?page=1&page_size=20
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)

**Response (200 OK):**
```json
{
    "count": 100,
    "next": "/api/posts?page=2",
    "previous": null,
    "results": [
        {
            "post_id": 1,
            "post_text": "Post content...",
            "post_datetime": "2024-01-15T10:30:00Z",
            "user": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com"
            },
            "header": "Post Header",
            "short": "Short description",
            "like_count": 10,
            "comment_count": 5,
            "liked": false,
            "primary_image_url": "https://...",
            "image_count": 2
        }
    ]
}
```

---

### Get Single Post
```http
GET /api/posts/{post_id}
```

**Response (200 OK):**
```json
{
    "post_id": 1,
    "post_text": "Post content...",
    "post_datetime": "2024-01-15T10:30:00Z",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    },
    "header": "Post Header",
    "short": "Short description",
    "like_count": 10,
    "comment_count": 5,
    "liked": false,
    "primary_image_url": "https://...",
    "image_count": 2
}
```

---

### Create Post
```http
POST /api/posts
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "header": "Post Header",
    "short": "Short description",
    "post_text": "Post content...",
    "user_id": 1
}
```

**Response (201 Created):**
```json
{
    "post_id": 1,
    "post_text": "Post content...",
    "post_datetime": "2024-01-15T10:30:00Z",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    },
    "header": "Post Header",
    "short": "Short description",
    "like_count": 0,
    "comment_count": 0,
    "liked": false
}
```

---

### Get Posts Feed (Lightweight)
```http
GET /api/posts/feed/?page_size=9
```

**Response (200 OK):**
```json
{
    "count": 100,
    "next": "/api/posts/feed/?page=2",
    "previous": null,
    "results": [
        {
            "post_id": 1,
            "post_datetime": "2024-01-15T10:30:00Z",
            "user": {
                "id": 1,
                "username": "john_doe"
            },
            "header": "Post Header",
            "short": "Short description",
            "like_count": 10,
            "comment_count": 5,
            "liked": false,
            "primary_image_url": "https://...",
            "image_count": 2
        }
    ]
}
```

**Note:** This endpoint excludes `post_text` and `comments` for better performance.

---

## Comment Endpoints

### List Comments
```http
GET /api/comments?post=1
```

**Query Parameters:**
- `post` (optional): Filter by post ID

**Response (200 OK):**
```json
{
    "results": [
        {
            "comment_id": 1,
            "post": 1,
            "user": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com"
            },
            "comment_datetime": "2024-01-15T10:30:00Z",
            "comment_text": "Comment text...",
            "like_count": 3
        }
    ]
}
```

---

### Get Single Comment
```http
GET /api/comments/{comment_id}
```

**Response (200 OK):**
```json
{
    "comment_id": 1,
    "post": 1,
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    },
    "comment_datetime": "2024-01-15T10:30:00Z",
    "comment_text": "Comment text...",
    "like_count": 3
}
```

---

### Create Comment
```http
POST /api/comments
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "post": 1,
    "user_id": 1,
    "comment_text": "Comment text..."
}
```

**Response (201 Created):**
```json
{
    "comment_id": 1,
    "post": 1,
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    },
    "comment_datetime": "2024-01-15T10:30:00Z",
    "comment_text": "Comment text...",
    "like_count": 0
}
```

---

### Update Comment
```http
PUT /api/comments/{comment_id}
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "comment_text": "Updated comment text..."
}
```

---

### Delete Comment
```http
DELETE /api/comments/{comment_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "message": "Comment deleted successfully"
}
```

---

## Like Endpoints

### Like Post
```http
POST /api/postlikes
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "post": 1,
    "user_id": 1
}
```

**Response (200 OK):**
```json
{
    "liked": true,
    "like_count": 11
}
```

---

### Unlike Post
```http
DELETE /api/postlikes/{post_id}/{user_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "message": "Post unliked successfully",
    "like_count": 10
}
```

---

### Like Comment
```http
POST /api/commentlikes
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "comment": 1,
    "user_id": 1
}
```

**Response (200 OK):**
```json
{
    "liked": true,
    "like_count": 4
}
```

---

### Unlike Comment
```http
DELETE /api/commentlikes/{comment_id}/{user_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "message": "Comment unliked successfully",
    "like_count": 3
}
```

---

## CloudDiary Endpoints

### List Cloud Diaries
```http
GET /api/clouddiary?page=1&page_size=20&user_id=1
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)
- `user_id` (optional): Filter by user ID

**Response (200 OK):**
```json
{
    "count": 50,
    "next": "/api/clouddiary?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Diary Title",
            "content": "Diary content...",
            "author": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com"
            },
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "is_public": true,
            "primary_image_url": "https://...",
            "image_count": 2
        }
    ]
}
```

---

### Get Single Cloud Diary
```http
GET /api/clouddiary/{diary_id}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "title": "Diary Title",
    "content": "Diary content...",
    "author": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "is_public": true,
    "primary_image_url": "https://...",
    "image_count": 2
}
```

---

### Create Cloud Diary
```http
POST /api/clouddiary
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "title": "Diary Title",
    "content": "Diary content...",
    "is_public": true,
    "author_id": 1
}
```

---

### Update Cloud Diary
```http
PUT /api/clouddiary/{diary_id}
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "title": "Updated Title",
    "content": "Updated content...",
    "is_public": false
}
```

---

### Delete Cloud Diary
```http
DELETE /api/clouddiary/{diary_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "message": "Cloud diary deleted successfully"
}
```

---

### Get User's Cloud Diaries
```http
GET /api/clouddiary/my-diaries?user_id=1&page=1&page_size=20
```

**Response (200 OK):**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [...]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
    "error": "Validation failed",
    "details": {
        "field_name": ["Error message"]
    }
}
```

### 401 Unauthorized
```json
{
    "error": "Email or Password is incorrect!"
}
```

### 404 Not Found
```json
{
    "error": "Post not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "An error occurred. Please try again."
}
```

---

## Rate Limiting

API endpoints may be rate-limited. Check response headers for rate limit information:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets

---

## Pagination

List endpoints support pagination:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

Response includes:
- `count`: Total number of items
- `next`: URL to next page (null if last page)
- `previous`: URL to previous page (null if first page)
- `results`: Array of items

---

For interactive API testing, use Swagger UI at `/api/docs/`.

