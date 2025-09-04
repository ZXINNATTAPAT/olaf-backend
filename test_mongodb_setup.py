#!/usr/bin/env python
"""
Test script to verify MongoDB and Redis setup.
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.development')
django.setup()

from django.core.cache import cache
from utils.mongodb import MongoDBManager, get_mongodb_stats
from authentication.models import Account
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mongodb_connection():
    """Test MongoDB connection and basic operations."""
    print("🔍 Testing MongoDB connection...")
    
    try:
        manager = MongoDBManager()
        print("✅ MongoDB connection successful")
        
        # Test database operations
        db = manager.get_database()
        collections = db.list_collection_names()
        print(f"📊 Available collections: {collections}")
        
        # Test creating a test document
        test_collection = db.test_collection
        test_doc = {"test": "MongoDB connection", "timestamp": "2024-01-01"}
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
        
        manager.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_redis_connection():
    """Test Redis connection and basic operations."""
    print("\n🔍 Testing Redis connection...")
    
    try:
        # Test cache operations
        cache.set('test_key', 'test_value', 30)
        value = cache.get('test_key')
        
        if value == 'test_value':
            print("✅ Redis connection and operations successful")
            cache.delete('test_key')
            return True
        else:
            print("❌ Redis value mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_django_models():
    """Test Django models with MongoDB."""
    print("\n🔍 Testing Django models...")
    
    try:
        # Test Account model
        account_count = Account.objects.count()
        print(f"✅ Account model accessible, count: {account_count}")
        
        # Test creating a test user (if none exists)
        if account_count == 0:
            print("📝 Creating test user...")
            test_user = Account.objects.create_user(
                email="test@example.com",
                username="testuser",
                first_name="Test",
                last_name="User",
                phone="0812345678",
                password="testpassword123"
            )
            print(f"✅ Test user created: {test_user.email}")
            
            # Clean up test user
            test_user.delete()
            print("✅ Test user cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Django models test failed: {e}")
        return False

def test_mongodb_indexes():
    """Test MongoDB index creation."""
    print("\n🔍 Testing MongoDB indexes...")
    
    try:
        manager = MongoDBManager()
        manager.create_indexes()
        print("✅ MongoDB indexes created successfully")
        manager.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB index creation failed: {e}")
        return False

def test_mongodb_stats():
    """Test MongoDB statistics retrieval."""
    print("\n🔍 Testing MongoDB statistics...")
    
    try:
        stats = get_mongodb_stats()
        print("✅ MongoDB statistics retrieved successfully")
        
        for collection, stat in stats.items():
            if stat:
                print(f"📊 {collection}: {stat['count']} documents")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB statistics failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting MongoDB and Redis setup tests...\n")
    
    tests = [
        ("MongoDB Connection", test_mongodb_connection),
        ("Redis Connection", test_redis_connection),
        ("Django Models", test_django_models),
        ("MongoDB Indexes", test_mongodb_indexes),
        ("MongoDB Statistics", test_mongodb_stats),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MongoDB and Redis setup is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the setup and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
