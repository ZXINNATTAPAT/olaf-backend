# MongoDB and Redis Setup Guide

This guide will help you set up MongoDB and Redis for the Olaf Backend application with HTTP-only cookies and optimized performance.

## Features

- ✅ **HTTP-only Cookies**: Secure JWT token storage in HTTP-only cookies
- ✅ **MongoDB Integration**: Full MongoDB support with optimized indexes
- ✅ **Redis Caching**: High-performance caching layer
- ✅ **Celery Background Tasks**: Asynchronous task processing
- ✅ **Connection Pooling**: Optimized database connections
- ✅ **Automatic Indexing**: MongoDB indexes for better query performance

## Prerequisites

- Python 3.9+
- pip
- MongoDB 6.0+
- Redis 6.0+
- Homebrew (macOS) or apt (Linux)

## Quick Setup

### 1. Run the Setup Script

```bash
# Make the script executable and run it
chmod +x scripts/setup_mongodb.sh
./scripts/setup_mongodb.sh
```

This script will:
- Install MongoDB and Redis
- Start the services
- Create the database and user
- Install Python dependencies
- Run Django migrations
- Create MongoDB indexes

### 2. Environment Configuration

Copy the example environment file and update it:

```bash
cp env.example .env
```

Update the `.env` file with your MongoDB and Redis configuration:

```env
# MongoDB Configuration
MONGODB_HOST=mongodb://localhost:27017/
MONGODB_DATABASE=olaf_backend
MONGODB_USERNAME=olaf_user
MONGODB_PASSWORD=olaf_password

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

## Manual Setup

### MongoDB Installation

#### macOS (using Homebrew)
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb/brew/mongodb-community
```

#### Linux (Ubuntu/Debian)
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Redis Installation

#### macOS (using Homebrew)
```bash
brew install redis
brew services start redis
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Python Dependencies

```bash
pip install -r requirements.txt
```

### Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create MongoDB indexes
python manage.py mongodb_setup --create-indexes
```

## Running the Application

### 1. Start Django Development Server

```bash
python manage.py runserver
```

### 2. Start Celery Worker (for background tasks)

```bash
celery -A mysite worker --loglevel=info
```

### 3. Start Celery Beat (for scheduled tasks)

```bash
celery -A mysite beat --loglevel=info
```

## MongoDB Management Commands

### Create Indexes
```bash
python manage.py mongodb_setup --create-indexes
```

### View Database Statistics
```bash
python manage.py mongodb_setup --stats
```

### Optimize Collections
```bash
python manage.py mongodb_setup --optimize
```

### Run All Optimizations
```bash
python manage.py mongodb_setup --all
```

## HTTP-Only Cookies Configuration

The application is already configured with secure HTTP-only cookies:

- **Access Token**: Stored in `access` cookie (5 minutes lifetime)
- **Refresh Token**: Stored in `refresh` cookie (24 hours lifetime)
- **Security**: HTTP-only, Secure, SameSite=None
- **CSRF Protection**: Enabled with token rotation

### Cookie Settings

```python
SIMPLE_JWT = {
    'AUTH_COOKIE': 'access',
    'AUTH_COOKIE_REFRESH': 'refresh',
    'AUTH_COOKIE_SECURE': True,
    'AUTH_COOKIE_HTTP_ONLY': True,
    'AUTH_COOKIE_SAMESITE': "None",
}
```

## Performance Optimizations

### 1. MongoDB Indexes

The following indexes are automatically created:

- **Users Collection**:
  - Email (unique)
  - Username (unique)
  - Created date (descending)

- **Posts Collection**:
  - Text search (title + content)
  - Created date (descending)
  - Author reference

### 2. Redis Caching

- **User Data**: Cached for 1 hour
- **Session Data**: Stored in Redis
- **Token Blacklist**: Cached for performance

### 3. Connection Pooling

- **MongoDB**: 50 max connections, 5 min connections
- **Redis**: Connection pooling with retry logic

## Background Tasks

Celery tasks are configured for:

- **Token Cleanup**: Hourly cleanup of expired tokens
- **MongoDB Optimization**: Daily collection optimization
- **User Data Backup**: Weekly backup of user data
- **Welcome Emails**: Asynchronous email sending
- **Activity Updates**: User activity tracking

## Monitoring and Logging

### Log Files
- Django logs: `logs/django.log`
- Application logs: Console and file output

### Health Checks
```bash
# Test MongoDB connection
mongosh --eval "db.runCommand('ping')"

# Test Redis connection
redis-cli ping
```

## Production Deployment

### Environment Variables

Set these environment variables in production:

```env
MONGODB_HOST=mongodb://your-mongodb-host:27017/
MONGODB_DATABASE=olaf_backend_prod
MONGODB_USERNAME=your-production-user
MONGODB_PASSWORD=your-secure-password
REDIS_URL=redis://your-redis-host:6379/1
```

### Security Considerations

1. **Use strong passwords** for MongoDB and Redis
2. **Enable authentication** on MongoDB
3. **Use SSL/TLS** for connections in production
4. **Set up firewall rules** to restrict access
5. **Regular backups** of MongoDB data

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check if MongoDB is running: `brew services list | grep mongodb`
   - Verify connection string in `.env`

2. **Redis Connection Failed**
   - Check if Redis is running: `brew services list | grep redis`
   - Test connection: `redis-cli ping`

3. **Index Creation Failed**
   - Run: `python manage.py mongodb_setup --create-indexes`
   - Check MongoDB logs for errors

4. **Celery Tasks Not Working**
   - Ensure Redis is running
   - Check Celery worker logs
   - Verify broker URL in settings

### Logs Location

- Django logs: `logs/django.log`
- MongoDB logs: `/usr/local/var/log/mongodb/mongo.log` (macOS)
- Redis logs: `/usr/local/var/log/redis.log` (macOS)

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify all services are running
3. Ensure environment variables are set correctly
4. Run the setup script again if needed
