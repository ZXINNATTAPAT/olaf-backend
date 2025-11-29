# Frontend Migration Guide - API Endpoints

## 📋 สรุป API Endpoints ที่ต้องแก้ไขใน Frontend

### ✅ Endpoints ที่ยังใช้ DRF (ไม่ต้องแก้ไข)
Endpoints เหล่านี้ยังใช้ Django REST Framework อยู่ ไม่ต้องแก้ไข:

1. **`GET /api/posts/feed/`** - Posts feed (lightweight, no comments)
   - Query params: `?page=1&page_size=20`
   - Response: `{count, next, previous, results: [...]}`

2. **`POST /api/posts/create-with-image/`** - Create post with image upload
   - FormData with image file
   - Response: Post object

---

## 🔄 Endpoints ที่เปลี่ยนเป็น Bolt API (ต้องแก้ไข)

### 1. Authentication Endpoints (`/api/auth/`)

#### ✅ ยังเหมือนเดิม (ไม่ต้องแก้ไข)
- `GET /api/auth/csrf` - Get CSRF token
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `GET /api/auth/user` - Get current user
- `GET /api/auth/check` - Check authentication status
- `POST /api/auth/refresh-token` - Refresh access token

**⚠️ หมายเหตุ:** Endpoints เหล่านี้ยังใช้ path เดิม แต่ตอนนี้ใช้ Bolt API แล้ว
- Response format อาจจะเหมือนเดิม แต่ควรทดสอบ
- Error response format อาจจะเปลี่ยน

---

### 2. Blog Posts Endpoints (`/api/posts/`)

#### ✅ เปลี่ยนเป็น Bolt API

**`GET /api/posts`** - List posts
- **Query Parameters:**
  - `page` (int, default: 1)
  - `page_size` (int, default: 20)
  - `limit` (int, optional) - Alias for `page_size`
  - `user` (int, optional) - Filter by user ID
- **Response:**
  ```json
  {
    "count": 100,
    "next": "/api/posts?page=2&page_size=20",
    "previous": null,
    "results": [
      {
        "post_id": 1,
        "post_text": "...",
        "post_datetime": "2024-01-15T10:30:00Z",
        "user": {
          "id": 1,
          "username": "john_doe",
          "email": "john@example.com"
        },
        "header": "...",
        "short": "...",
        "like_count": 10,
        "comment_count": 5,
        "liked": false,
        "image_url": "...",
        "image_secure_url": "...",
        "primary_image_url": "...",
        "image_count": 3
      }
    ]
  }
  ```

**`GET /api/posts/{post_id}`** - Get single post
- **Path Parameter:** `post_id` (int)
- **Response:** Single post object (same structure as above)

**`POST /api/posts`** - Create post
- **Request Body:**
  ```json
  {
    "post_text": "Post content",
    "header": "Post header",
    "short": "Short description"
  }
  ```
- **Response:** Created post object

---

### 3. Comments Endpoints (`/api/comments/`)

#### ✅ เปลี่ยนเป็น Bolt API

**`GET /api/comments`** - List comments
- **Query Parameters:**
  - `post` (int, optional) - Filter by post ID
  - `page` (int, default: 1)
  - `page_size` (int, default: 20)
- **Response:**
  ```json
  {
    "count": 50,
    "next": null,
    "previous": null,
    "results": [
      {
        "comment_id": 1,
        "post": 1,
        "user": {
          "id": 1,
          "username": "john_doe",
          "email": "john@example.com"
        },
        "comment_text": "Great post!",
        "comment_datetime": "2024-01-15T10:30:00Z",
        "like_count": 5,
        "liked": false
      }
    ]
  }
  ```

**`GET /api/comments/{comment_id}`** - Get single comment
- **Path Parameter:** `comment_id` (int)
- **Response:** Single comment object

**`POST /api/comments`** - Create comment
- **Request Body:**
  ```json
  {
    "post": 1,
    "comment_text": "This is a comment"
  }
  ```
- **Response:** Created comment object

**`PUT /api/comments/{comment_id}`** - Update comment
- **Path Parameter:** `comment_id` (int)
- **Request Body:**
  ```json
  {
    "comment_text": "Updated comment text"
  }
  ```
- **Response:** Updated comment object

**`DELETE /api/comments/{comment_id}`** - Delete comment
- **Path Parameter:** `comment_id` (int)
- **Response:** `204 No Content` or success message

---

### 4. Likes Endpoints

#### ✅ เปลี่ยนเป็น Bolt API

**`POST /api/postlikes`** - Like a post
- **Request Body:**
  ```json
  {
    "post": 1,
    "user": 1
  }
  ```
- **Response:** Like object or success message

**`DELETE /api/postlikes/{post_id}/{user_id}`** - Unlike a post
- **Path Parameters:**
  - `post_id` (int)
  - `user_id` (int)
- **Response:** `204 No Content` or success message

**`POST /api/commentlikes`** - Like a comment
- **Request Body:**
  ```json
  {
    "comment": 1,
    "user": 1
  }
  ```
- **Response:** Like object or success message

**`DELETE /api/commentlikes/{comment_id}/{user_id}`** - Unlike a comment
- **Path Parameters:**
  - `comment_id` (int)
  - `user_id` (int)
- **Response:** `204 No Content` or success message

---

### 5. CloudDiary Endpoints (`/api/clouddiary/`)

#### ✅ เปลี่ยนเป็น Bolt API

**`GET /api/clouddiary/`** - List cloud diaries
- **Query Parameters:**
  - `page` (int, default: 1)
  - `page_size` (int, default: 20)
- **Response:**
  ```json
  {
    "count": 20,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "user": {
          "id": 1,
          "username": "john_doe",
          "email": "john@example.com"
        },
        "title": "My Diary",
        "content": "...",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "images": [...]
      }
    ]
  }
  ```

**`GET /api/clouddiary/{diary_id}`** - Get single diary
- **Path Parameter:** `diary_id` (int)
- **Response:** Single diary object

**`POST /api/clouddiary/`** - Create diary
- **Request Body:**
  ```json
  {
    "title": "New Diary",
    "content": "Diary content"
  }
  ```
- **Response:** Created diary object

**`PUT /api/clouddiary/{diary_id}`** - Update diary
- **Path Parameter:** `diary_id` (int)
- **Request Body:**
  ```json
  {
    "title": "Updated Title",
    "content": "Updated content"
  }
  ```
- **Response:** Updated diary object

**`DELETE /api/clouddiary/{diary_id}`** - Delete diary
- **Path Parameter:** `diary_id` (int)
- **Response:** `204 No Content` or success message

**`GET /api/clouddiary/my-diaries`** - Get user's diaries
- **Response:** List of user's diaries (same format as list)

---

## 🔍 สิ่งที่ต้องตรวจสอบใน Frontend

### 1. URL Paths
- ✅ ตรวจสอบว่า paths ตรงกับ Bolt API routes
- ✅ Path parameters ใช้ `{id}` แทน `<int:id>` (Bolt ใช้ `{id}`)
- ✅ Trailing slashes: Bolt API ไม่มี trailing slash (ยกเว้น `/api/clouddiary/`)

### 2. Request Format
- ✅ Content-Type: `application/json` สำหรับ POST/PUT
- ✅ Query parameters: ใช้ snake_case (`page_size`, `post_id`)
- ✅ Request body: ใช้ snake_case (`post_text`, `comment_text`)

### 3. Response Format
- ✅ Pagination: `{count, next, previous, results}`
- ✅ Error responses: อาจจะเปลี่ยน format (ควรทดสอบ)
- ✅ Status codes: 200, 201, 204, 400, 401, 404, 500

### 4. Authentication
- ✅ CSRF token: ยังต้องใช้ `X-CSRFToken` header
- ✅ Cookies: `access`, `refresh`, `csrftoken` ยังใช้เหมือนเดิม
- ✅ Authorization: อาจจะต้องใช้ `Authorization: Bearer <token>` header

### 5. Error Handling
- ✅ ตรวจสอบ error response format
- ✅ Handle 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), 500 (Internal Server Error)

---

## 📝 Checklist สำหรับ Frontend Migration

### Authentication
- [ ] Test `GET /api/auth/csrf`
- [ ] Test `POST /api/auth/login`
- [ ] Test `POST /api/auth/register`
- [ ] Test `POST /api/auth/logout`
- [ ] Test `GET /api/auth/user`
- [ ] Test `GET /api/auth/check`
- [ ] Test `POST /api/auth/refresh-token`

### Blog Posts
- [ ] Test `GET /api/posts` (with pagination)
- [ ] Test `GET /api/posts?user=1` (filter by user)
- [ ] Test `GET /api/posts/{post_id}`
- [ ] Test `POST /api/posts`
- [ ] Test `GET /api/posts/feed/` (DRF endpoint - should still work)

### Comments
- [ ] Test `GET /api/comments`
- [ ] Test `GET /api/comments?post=1` (filter by post)
- [ ] Test `GET /api/comments/{comment_id}`
- [ ] Test `POST /api/comments`
- [ ] Test `PUT /api/comments/{comment_id}`
- [ ] Test `DELETE /api/comments/{comment_id}`

### Likes
- [ ] Test `POST /api/postlikes`
- [ ] Test `DELETE /api/postlikes/{post_id}/{user_id}`
- [ ] Test `POST /api/commentlikes`
- [ ] Test `DELETE /api/commentlikes/{comment_id}/{user_id}`

### CloudDiary
- [ ] Test `GET /api/clouddiary/`
- [ ] Test `GET /api/clouddiary/{diary_id}`
- [ ] Test `POST /api/clouddiary/`
- [ ] Test `PUT /api/clouddiary/{diary_id}`
- [ ] Test `DELETE /api/clouddiary/{diary_id}`
- [ ] Test `GET /api/clouddiary/my-diaries`

---

## 🚀 Base URLs

- **Development**: `http://localhost:8000/api/`
- **Production**: `https://web-production-ba20a.up.railway.app/api/`

---

## 📚 เอกสารเพิ่มเติม

- OpenAPI Schema: `https://web-production-ba20a.up.railway.app/api/openapi.json`
- Swagger UI: `https://web-production-ba20a.up.railway.app/api/docs/`

