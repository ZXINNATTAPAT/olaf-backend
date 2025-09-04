#!/bin/bash

# MongoDB and Redis Setup Script for Olaf Backend
# This script sets up MongoDB and Redis for the application

set -e

echo "🚀 Setting up MongoDB and Redis for Olaf Backend..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Detected macOS system"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew is not installed. Please install Homebrew first."
        echo "Visit: https://brew.sh/"
        exit 1
    fi
    
    # Install MongoDB
    print_status "Installing MongoDB..."
    if ! command -v mongod &> /dev/null; then
        brew tap mongodb/brew
        brew install mongodb-community
        print_status "MongoDB installed successfully"
    else
        print_warning "MongoDB is already installed"
    fi
    
    # Install Redis
    print_status "Installing Redis..."
    if ! command -v redis-server &> /dev/null; then
        brew install redis
        print_status "Redis installed successfully"
    else
        print_warning "Redis is already installed"
    fi
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "Detected Linux system"
    
    # Update package list
    sudo apt-get update
    
    # Install MongoDB
    print_status "Installing MongoDB..."
    if ! command -v mongod &> /dev/null; then
        wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
        echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
        sudo apt-get update
        sudo apt-get install -y mongodb-org
        print_status "MongoDB installed successfully"
    else
        print_warning "MongoDB is already installed"
    fi
    
    # Install Redis
    print_status "Installing Redis..."
    if ! command -v redis-server &> /dev/null; then
        sudo apt-get install -y redis-server
        print_status "Redis installed successfully"
    else
        print_warning "Redis is already installed"
    fi
    
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

# Start MongoDB service
print_status "Starting MongoDB service..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start mongodb/brew/mongodb-community
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo systemctl start mongod
    sudo systemctl enable mongod
fi

# Start Redis service
print_status "Starting Redis service..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start redis
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
fi

# Wait for services to start
print_status "Waiting for services to start..."
sleep 5

# Test MongoDB connection
print_status "Testing MongoDB connection..."
if mongosh --eval "db.runCommand('ping')" --quiet; then
    print_status "MongoDB is running successfully"
else
    print_error "Failed to connect to MongoDB"
    exit 1
fi

# Test Redis connection
print_status "Testing Redis connection..."
if redis-cli ping | grep -q "PONG"; then
    print_status "Redis is running successfully"
else
    print_error "Failed to connect to Redis"
    exit 1
fi

# Create MongoDB database and user (optional)
print_status "Setting up MongoDB database..."
mongosh --eval "
use olaf_backend;
db.createUser({
  user: 'olaf_user',
  pwd: 'olaf_password',
  roles: [
    { role: 'readWrite', db: 'olaf_backend' }
  ]
});
" --quiet

print_status "MongoDB user created successfully"

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Python dependencies installed successfully"
else
    print_warning "requirements.txt not found"
fi

# Run Django migrations
print_status "Running Django migrations..."
python manage.py makemigrations
python manage.py migrate

# Create MongoDB indexes
print_status "Creating MongoDB indexes..."
python manage.py mongodb_setup --create-indexes

print_status "✅ Setup completed successfully!"
print_status "MongoDB is running on: mongodb://localhost:27017/"
print_status "Redis is running on: redis://localhost:6379/"
print_status "Database: olaf_backend"
print_status "User: olaf_user"

echo ""
print_status "Next steps:"
echo "1. Update your .env file with the MongoDB and Redis configuration"
echo "2. Start the Django development server: python manage.py runserver"
echo "3. Start Celery worker: celery -A mysite worker --loglevel=info"
echo "4. Start Celery beat: celery -A mysite beat --loglevel=info"
