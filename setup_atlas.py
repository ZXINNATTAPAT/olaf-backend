#!/usr/bin/env python3
"""
Script to help setup MongoDB Atlas connection and migrate data.
"""
import os
import pymongo
from pymongo import MongoClient
import json
from datetime import datetime

def check_atlas_connection():
    """Check if Atlas connection is configured."""
    print("🔍 Checking MongoDB Atlas Configuration")
    print("=" * 50)
    
    # Check environment variables
    atlas_uri = os.environ.get('MONGODB_ATLAS_URI', '')
    atlas_username = os.environ.get('MONGODB_USERNAME', '')
    atlas_password = os.environ.get('MONGODB_PASSWORD', '')
    
    print(f"Atlas URI: {'✅ Set' if atlas_uri and 'cluster.mongodb.net' in atlas_uri else '❌ Not set or invalid'}")
    print(f"Username: {'✅ Set' if atlas_username else '❌ Not set'}")
    print(f"Password: {'✅ Set' if atlas_password else '❌ Not set'}")
    print()
    
    if not atlas_uri or 'username:password@cluster.mongodb.net' in atlas_uri:
        print("⚠️  MongoDB Atlas not properly configured!")
        print("\n📋 Steps to setup Atlas:")
        print("1. Go to https://www.mongodb.com/atlas")
        print("2. Create a free cluster (M0)")
        print("3. Create database user")
        print("4. Add IP address (0.0.0.0/0 for development)")
        print("5. Get connection string")
        print("6. Update .env file with your Atlas credentials")
        return False
    
    return True

def test_atlas_connection():
    """Test connection to MongoDB Atlas."""
    try:
        atlas_uri = os.environ.get('MONGODB_ATLAS_URI', '')
        if not atlas_uri:
            print("❌ MONGODB_ATLAS_URI not set")
            return False
        
        print("🔗 Testing Atlas connection...")
        client = MongoClient(atlas_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")
        
        # Get database
        db = client['olaf_backend']
        
        # Check collections
        collections = db.list_collection_names()
        print(f"📚 Collections in Atlas: {collections}")
        
        # Show stats
        stats = db.command("dbStats")
        print(f"📊 Documents: {stats['objects']}")
        print(f"💾 Data Size: {stats['dataSize']:,} bytes")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Atlas connection failed: {e}")
        return False

def migrate_to_atlas():
    """Migrate data from local MongoDB to Atlas."""
    try:
        print("🚀 Starting migration to Atlas...")
        
        # Connect to local MongoDB
        local_client = MongoClient('mongodb://localhost:27017/')
        local_db = local_client['olaf_backend']
        
        # Connect to Atlas
        atlas_uri = os.environ.get('MONGODB_ATLAS_URI', '')
        atlas_client = MongoClient(atlas_uri)
        atlas_db = atlas_client['olaf_backend']
        
        # Get collections from local
        collections = local_db.list_collection_names()
        
        for collection_name in collections:
            print(f"📦 Migrating {collection_name}...")
            
            # Get all documents from local
            local_collection = local_db[collection_name]
            documents = list(local_collection.find())
            
            if documents:
                # Insert into Atlas
                atlas_collection = atlas_db[collection_name]
                atlas_collection.insert_many(documents)
                print(f"✅ Migrated {len(documents)} documents to {collection_name}")
            else:
                print(f"⚠️  No documents in {collection_name}")
        
        # Create indexes in Atlas
        print("🔍 Creating indexes in Atlas...")
        from utils.mongodb import MongoDBManager
        manager = MongoDBManager()
        manager.create_indexes()
        manager.close()
        
        local_client.close()
        atlas_client.close()
        
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main function."""
    print("🌐 MongoDB Atlas Setup Helper")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check configuration
    if not check_atlas_connection():
        return
    
    # Test connection
    if test_atlas_connection():
        print("\n🎉 Atlas is already working!")
    else:
        print("\n🔄 Would you like to migrate data to Atlas? (y/n)")
        choice = input().lower()
        if choice == 'y':
            migrate_to_atlas()

if __name__ == "__main__":
    main()
