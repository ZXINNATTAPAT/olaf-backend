#!/bin/bash

# Development setup script for Olaf Backend

echo "Setting up Olaf Backend for development..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "Please edit .env file with your configuration"
fi

# Create logs directory
mkdir -p logs

# Run migrations
echo "Running database migrations..."
python manage_dev.py makemigrations
python manage_dev.py migrate

# Create superuser (optional)
echo "Would you like to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage_dev.py createsuperuser
fi

echo "Development setup complete!"
echo "To start the development server, run: python manage_dev.py runserver"
