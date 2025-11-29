# Olaf Backend API

High-performance REST API service built with Django and Django-Bolt.

## 🚀 Features

- **Django-Bolt Framework**: High-performance async API framework powered by Rust
- **JWT Authentication**: Secure token-based authentication with HTTP-only cookies
- **OpenAPI/Swagger Documentation**: Interactive API documentation
- **PostgreSQL Database**: Production-ready database support
- **Cloudinary Integration**: Image upload and management
- **CORS Support**: Cross-origin resource sharing configured

## 📋 Requirements

- Python 3.10+
- PostgreSQL (or SQLite for development)
- Rust toolchain (for Django-Bolt)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd olaf-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy .env.example to .env and configure
cp .env.example .env
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of CORS origins
- `CLOUDINARY_URL`: Cloudinary configuration

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

## 🏃 Running the Server

### Development
```bash
python manage.py runserver
```

### Production
```bash
gunicorn mysite.wsgi --bind 0.0.0.0:8000
```

## 📚 API Documentation

### Swagger UI
Access interactive API documentation at:
- **Development**: http://localhost:8000/api/docs/
- **Production**: https://web-production-ba20a.up.railway.app/api/docs/

### OpenAPI Schema
- **JSON Schema**: http://localhost:8000/api/openapi.json
- **BoltAPI Schema**: http://localhost:8000/api/schema

## 🔌 API Endpoints

### Base URLs
- **Development**: `http://localhost:8000/api/`
- **Production**: `https://web-production-ba20a.up.railway.app/api/`

### Authentication (`/api/auth/`)
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `GET /api/auth/user` - Get current user
- `GET /api/auth/check` - Check authentication status
- `GET /api/auth/csrf` - Get CSRF token
- `POST /api/auth/refresh-token` - Refresh access token

### Blog (`/api/posts/`)
- `GET /api/posts` - List posts (with pagination)
- `GET /api/posts/{post_id}` - Get single post
- `POST /api/posts` - Create post
- `GET /api/posts/feed/` - Get posts feed (lightweight, no comments)

### Comments (`/api/comments/`)
- `GET /api/comments` - List comments
- `GET /api/comments/{comment_id}` - Get single comment
- `POST /api/comments` - Create comment
- `PUT /api/comments/{comment_id}` - Update comment
- `DELETE /api/comments/{comment_id}` - Delete comment

### Likes (`/api/postlikes/`, `/api/commentlikes/`)
- `POST /api/postlikes` - Like a post
- `DELETE /api/postlikes/{post_id}/{user_id}` - Unlike a post
- `POST /api/commentlikes` - Like a comment
- `DELETE /api/commentlikes/{comment_id}/{user_id}` - Unlike a comment

### CloudDiary (`/api/clouddiary/`)
- `GET /api/clouddiary` - List cloud diaries
- `GET /api/clouddiary/{diary_id}` - Get single diary
- `POST /api/clouddiary` - Create diary
- `PUT /api/clouddiary/{diary_id}` - Update diary
- `DELETE /api/clouddiary/{diary_id}` - Delete diary
- `GET /api/clouddiary/my-diaries` - Get user's diaries

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Tokens are stored in HTTP-only cookies for security.

### Authentication Flow

1. **Get CSRF Token**
```http
GET /api/auth/csrf/
```

2. **Login**
```http
POST /api/auth/login
Content-Type: application/json
X-CSRFToken: <csrf_token>

{
  "email": "user@example.com",
  "password": "password123"
}
```

3. **Use Access Token**
```http
GET /api/auth/user
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

### Cookie Settings
- `access`: Access token (HttpOnly, expires in 1 hour)
- `refresh`: Refresh token (HttpOnly, expires in 7 days)
- `csrftoken`: CSRF token

## 📁 Project Structure

```
olaf-backend/
├── authentication/      # Authentication app
│   ├── bolt_api.py     # Bolt API routes (login, register, etc.)
│   ├── models.py       # User models
│   ├── serializers.py  # DRF serializers
│   └── services.py     # Auth services (token generation, etc.)
├── blog/               # Blog app
│   ├── bolt_api.py     # Bolt API routes (posts, comments, likes)
│   ├── models.py       # Post, Comment, Like models
│   └── serializers.py  # DRF serializers
├── clouddiary/         # CloudDiary app
│   ├── bolt_api.py     # Bolt API routes
│   └── models.py       # CloudDiary models
├── shared_images/      # Shared images app
│   └── models.py       # SharedImage model
├── mysite/             # Django project settings
│   ├── bolt_urls.py    # Bolt API URL routing
│   ├── settings.py     # Django settings
│   └── urls.py         # Main URL configuration
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🏗️ Architecture

### API Framework
- **Django-Bolt**: Primary API framework for high-performance endpoints
- **Django REST Framework**: Fallback for complex endpoints (image uploads, etc.)

### Database
- **PostgreSQL**: Production database
- **SQLite**: Development database (default)

### Image Storage
- **Cloudinary**: Cloud-based image storage and CDN

## 🔧 Configuration

### CORS Settings
Configure allowed origins in `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-frontend-domain.com",
]
```

### JWT Settings
JWT configuration in `settings.py`:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_COOKIE': 'access',
    'AUTH_COOKIE_REFRESH': 'refresh',
}
```

## 📝 Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Accessing Admin (if enabled)
```bash
# Note: Admin is disabled by default. Use Swagger UI instead.
```

## 🚢 Deployment

### Railway Deployment

The project is configured for Railway deployment. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

#### Quick Start:
1. Push code to GitHub
2. Create new project on Railway
3. Connect GitHub repository
4. Add environment variables (see below)
5. Add PostgreSQL service (optional, Railway provides `DATABASE_URL`)
6. Deploy!

#### Required Environment Variables:
- `SECRET_KEY`: Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Your Railway domain (e.g., `your-app.railway.app`)
- `DATABASE_URL`: Auto-provided by Railway if using PostgreSQL service
- `CORS_ALLOWED_ORIGINS`: Frontend domain(s) (comma-separated)
- `CLOUDINARY_URL`: Cloudinary configuration (if using)

#### Files for Railway:
- `Procfile`: Defines web and release commands
- `runtime.txt`: Specifies Python version (3.10.12)
- `requirements.txt`: Python dependencies
- `railway.json`: Railway configuration (optional)

For detailed deployment guide, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

## 📞 Support

For issues and questions, please open an issue on GitHub.

