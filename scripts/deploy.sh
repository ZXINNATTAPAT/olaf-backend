#!/bin/bash

# Production deployment script for Olaf Backend

echo "Deploying Olaf Backend to production..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create it with production settings."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage_prod.py makemigrations
python manage_prod.py migrate

# Collect static files
echo "Collecting static files..."
python manage_prod.py collectstatic --noinput

# Create logs directory
mkdir -p logs

echo "Production deployment complete!"
echo "Make sure to configure your web server (nginx, apache) to serve static files."
