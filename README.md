# Olaf Backend API

A Django REST Framework API for a social media/blog platform with authentication, posts, comments, and likes functionality.

## Features

- **User Authentication**: JWT-based authentication with cookie support
- **User Management**: Custom user model with profile information
- **Posts**: Create, read, update, delete posts with image support
- **Comments**: Comment on posts with like functionality
- **Likes**: Like posts and comments
- **Image Upload**: Support for image uploads with automatic resizing
- **CORS Support**: Configured for frontend integration
- **Environment-based Settings**: Separate settings for development and production

## Project Structure

```
olaf-backend/
├── authentication/          # User authentication app
│   ├── models.py           # Custom user model
│   ├── views.py            # Authentication views
│   ├── serializers.py      # User serializers
│   └── urls.py             # Authentication URLs
├── blog/                   # Blog/posts app
│   ├── models.py           # Post, Comment, Like models
│   ├── views.py            # Blog views
│   ├── serializers.py      # Blog serializers
│   └── urls.py             # Blog URLs
├── mysite/                 # Main project settings
│   ├── settings/           # Environment-based settings
│   │   ├── base.py         # Base settings
│   │   ├── development.py  # Development settings
│   │   └── production.py   # Production settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── utils/                  # Utility functions
│   ├── response.py         # Custom API responses
│   ├── validators.py       # Custom validators
│   ├── helpers.py          # Helper functions
│   ├── exceptions.py       # Custom exceptions
│   └── permissions.py      # Custom permissions
├── media/                  # Media files
├── static/                 # Static files
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables example
└── README.md              # This file
```

## Installation

### Prerequisites

- Python 3.9+
- pip
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd olaf-backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database
DATABASE_URL=sqlite:///db.sqlite3

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://olafs.netlify.app
CSRF_TRUSTED_ORIGINS=http://localhost:3000,https://olafs.netlify.app

# Email Settings (for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=5
JWT_REFRESH_TOKEN_LIFETIME=1440

# File Upload Settings
MAX_FILE_SIZE_MB=10
ALLOWED_IMAGE_TYPES=jpg,jpeg,png,gif

# Logging
LOG_LEVEL=INFO
```

## API Endpoints

### Authentication

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/refresh-token/` - Refresh JWT token
- `GET /api/auth/user/` - Get current user info

### Posts

- `GET /api/posts/` - List all posts
- `POST /api/posts/` - Create new post
- `GET /api/posts/{id}/` - Get specific post
- `PUT /api/posts/{id}/` - Update post
- `DELETE /api/posts/{id}/` - Delete post

### Comments

- `GET /api/comments/` - List all comments
- `POST /api/comments/` - Create new comment
- `GET /api/comments/{id}/` - Get specific comment
- `PUT /api/comments/{id}/` - Update comment
- `DELETE /api/comments/{id}/` - Delete comment

### Likes

- `POST /api/postlikes/` - Like a post
- `DELETE /api/postlikes/{post_id}/{user_id}/` - Unlike a post
- `POST /api/commentlikes/` - Like a comment
- `DELETE /api/commentlikes/{comment_id}/{user_id}/` - Unlike a comment

### Users

- `GET /api/users/` - List all users
- `GET /api/users/{id}/` - Get specific user

## API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Success",
  "data": {
    // Response data
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "data": {
    // Error details
  },
  "error_code": "ErrorType"
}
```

## Models

### Account (User)
- `email` - User email (unique)
- `username` - Username (3-50 characters)
- `first_name` - First name
- `last_name` - Last name
- `phone` - Phone number (Thai format)
- `is_active` - Account status
- `created_at` - Account creation date
- `updated_at` - Last update date

### Post
- `post_id` - Primary key
- `header` - Post title
- `short` - Short description
- `post_text` - Main content
- `user` - Author (ForeignKey to Account)
- `image` - Post image
- `is_published` - Publication status
- `post_datetime` - Creation date
- `updated_at` - Last update date

### Comment
- `comment_id` - Primary key
- `post` - Related post (ForeignKey)
- `user` - Commenter (ForeignKey to Account)
- `comment_text` - Comment content
- `is_edited` - Edit status
- `comment_datetime` - Creation date
- `updated_at` - Last update date

### PostLike/CommentLike
- `post/comment` - Related object (ForeignKey)
- `user` - User who liked (ForeignKey to Account)
- `created_at` - Like creation date

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
The project follows PEP 8 style guidelines. Use a linter like `flake8` or `black` for code formatting.

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Deployment

### Production Settings
Set the following environment variables for production:

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-production-database-url
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### Static Files
```bash
python manage.py collectstatic
```

### Database
For production, consider using PostgreSQL or MySQL instead of SQLite.

## Security Features

- JWT-based authentication
- CORS configuration
- CSRF protection
- Input validation
- File upload restrictions
- Password strength validation
- Phone number validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please contact [your-email@example.com] or create an issue in the repository.
