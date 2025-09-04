#!/usr/bin/env python3
"""
Test script for user and blog creation flow.
"""
import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"

def test_user_registration():
    """Test user registration."""
    print("👤 Testing User Registration")
    print("=" * 40)
    
    # Test data
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "0812345678",
        "password": "testpassword123",
        "password2": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register/", json=user_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ User registration successful!")
            return True
        else:
            print("❌ User registration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_user_login():
    """Test user login."""
    print("\n🔐 Testing User Login")
    print("=" * 40)
    
    login_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ User login successful!")
            # Extract cookies for future requests
            cookies = response.cookies
            return cookies
        else:
            print("❌ User login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_blog_creation(cookies):
    """Test blog post creation."""
    print("\n📝 Testing Blog Post Creation")
    print("=" * 40)
    
    blog_data = {
        "title": "Test Blog Post",
        "content": "This is a test blog post created through API.",
        "is_published": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/blog/posts/", json=blog_data, cookies=cookies)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Blog post creation successful!")
            return True
        else:
            print("❌ Blog post creation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_posts():
    """Test getting all blog posts."""
    print("\n📚 Testing Get Blog Posts")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/blog/posts/")
        
        print(f"Status Code: {response.status_code}")
        posts = response.json()
        
        if response.status_code == 200:
            print(f"✅ Found {len(posts)} blog posts!")
            for i, post in enumerate(posts, 1):
                print(f"  {i}. {post.get('title', 'No title')} - {post.get('author', 'No author')}")
            return True
        else:
            print("❌ Failed to get blog posts!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_users():
    """Test getting all users."""
    print("\n👥 Testing Get Users")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/blog/users/")
        
        print(f"Status Code: {response.status_code}")
        users = response.json()
        
        if response.status_code == 200:
            print(f"✅ Found {len(users)} users!")
            for i, user in enumerate(users, 1):
                print(f"  {i}. {user.get('username', 'No username')} - {user.get('email', 'No email')}")
            return True
        else:
            print("❌ Failed to get users!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_mongodb_data():
    """Check data in MongoDB."""
    print("\n🗄️ Checking MongoDB Data")
    print("=" * 40)
    
    try:
        # Run the check script
        import subprocess
        result = subprocess.run(['python3', 'check_mongodb.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ MongoDB data check completed!")
            print(result.stdout)
        else:
            print("❌ MongoDB data check failed!")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error checking MongoDB: {e}")

def main():
    """Main test function."""
    print("🚀 Testing User and Blog Creation Flow")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test user registration
    if not test_user_registration():
        print("❌ User registration failed, stopping tests")
        return
    
    # Test user login
    cookies = test_user_login()
    if not cookies:
        print("❌ User login failed, stopping tests")
        return
    
    # Test blog creation
    if not test_blog_creation(cookies):
        print("❌ Blog creation failed")
    
    # Test getting posts
    test_get_posts()
    
    # Test getting users
    test_get_users()
    
    # Check MongoDB data
    check_mongodb_data()
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    main()
