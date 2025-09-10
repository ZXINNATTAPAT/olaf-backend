#!/usr/bin/env python3
"""
Test script for image upload API
"""
import requests
import json

# Configuration
BASE_URL = "https://olaf-backend.onrender.com"
# BASE_URL = "http://localhost:8000"  # For local testing

def test_image_upload():
    # Test data
    post_id = 4
    
    # Headers
    headers = {
        'Authorization': 'Bearer YOUR_JWT_TOKEN_HERE',  # Replace with actual token
        'Content-Type': 'multipart/form-data'
    }
    
    # Test image data (you need to provide actual image file)
    files = {
        'image': ('test_image.jpg', open('test_image.jpg', 'rb'), 'image/jpeg')
    }
    
    data = {
        'caption': 'Test image upload',
        'is_primary': True,
        'sort_order': 0
    }
    
    # Make request
    url = f"{BASE_URL}/api/posts/{post_id}/upload-image/"
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Upload successful!")
        else:
            print("❌ Upload failed!")
            
    except Exception as e:
        print(f"Error: {e}")

def test_get_posts():
    """Test getting posts to verify authentication"""
    headers = {
        'Authorization': 'Bearer YOUR_JWT_TOKEN_HERE',  # Replace with actual token
    }
    
    url = f"{BASE_URL}/api/posts/"
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    print("1. Testing GET posts...")
    test_get_posts()
    print("\n2. Testing image upload...")
    test_image_upload()
