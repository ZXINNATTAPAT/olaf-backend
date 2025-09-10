#!/usr/bin/env python3
"""
Simple test for create_post_with_image endpoint
"""
import requests
import json

# Test data
BASE_URL = "https://olaf-backend.onrender.com"
# BASE_URL = "http://localhost:8000"  # For local testing

JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU3NTAxODU1LCJpYXQiOjE3NTc0OTgyNTUsImp0aSI6IjgzMjQ5NTAyMzI2NTQ1ZjNhZjVmMmIwNjc1MzE0M2Q1IiwidXNlcl9pZCI6MX0.HxT_rSQ-9kV9hJfs2pF1BujgIJ9vPbVyIqRG4UbE1WA"

def test_create_post():
    print("Testing create post with image endpoint...")
    
    # Test data
    post_data = {
        "header": "Test Post",
        "short": "Test Description", 
        "post_text": "This is a test post",
        "user_id": 1,
        "image_url": "https://res.cloudinary.com/dm02oprw0/image/upload/v1757496777/olaf-posts/post_1757496743339_bbl07btam.png",
        "caption": "Test image",
        "is_primary": True,
        "sort_order": 0
    }
    
    headers = {
        'Authorization': f'Bearer {JWT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/posts/create-with-image/",
            json=post_data,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text}")
        
        if response.status_code == 201:
            print("✅ Success!")
        else:
            print("❌ Failed!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_post()
