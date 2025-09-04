#!/usr/bin/env python3
"""
Script to help update MongoDB Atlas configuration.
"""
import os
import re

def update_env_file():
    """Update .env file with Atlas configuration."""
    print("🔧 MongoDB Atlas Configuration Helper")
    print("=" * 50)
    
    # Read current .env file
    try:
        with open('.env', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ .env file not found!")
        return
    
    print("📋 Current configuration:")
    print("-" * 30)
    
    # Show current values
    atlas_uri = re.search(r'MONGODB_ATLAS_URI=(.+)', content)
    username = re.search(r'MONGODB_USERNAME=(.+)', content)
    password = re.search(r'MONGODB_PASSWORD=(.+)', content)
    
    print(f"Atlas URI: {atlas_uri.group(1) if atlas_uri else 'Not set'}")
    print(f"Username: {username.group(1) if username else 'Not set'}")
    print(f"Password: {'*' * len(password.group(1)) if password else 'Not set'}")
    print()
    
    print("📝 Please provide your Atlas credentials:")
    print("(Press Enter to keep current value)")
    print()
    
    # Get new values
    new_uri = input("MongoDB Atlas URI: ").strip()
    new_username = input("Username: ").strip()
    new_password = input("Password: ").strip()
    
    # Update content
    if new_uri:
        content = re.sub(r'MONGODB_ATLAS_URI=.+', f'MONGODB_ATLAS_URI={new_uri}', content)
    
    if new_username:
        content = re.sub(r'MONGODB_USERNAME=.+', f'MONGODB_USERNAME={new_username}', content)
    
    if new_password:
        content = re.sub(r'MONGODB_PASSWORD=.+', f'MONGODB_PASSWORD={new_password}', content)
    
    # Write back to file
    with open('.env', 'w') as f:
        f.write(content)
    
    print("\n✅ Configuration updated!")
    print("\n🧪 Testing connection...")
    
    # Test connection
    test_atlas_connection()

def test_atlas_connection():
    """Test Atlas connection."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        import pymongo
        from pymongo import MongoClient
        
        atlas_uri = os.environ.get('MONGODB_ATLAS_URI', '')
        if not atlas_uri or 'username:password@cluster.mongodb.net' in atlas_uri:
            print("❌ Please update your Atlas URI first!")
            return False
        
        print("🔗 Connecting to Atlas...")
        client = MongoClient(atlas_uri, serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")
        
        # Get database
        db = client['olaf_backend']
        
        # Check collections
        collections = db.list_collection_names()
        print(f"📚 Collections: {collections}")
        
        # Show stats
        stats = db.command("dbStats")
        print(f"📊 Documents: {stats['objects']}")
        print(f"💾 Data Size: {stats['dataSize']:,} bytes")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your Atlas URI format")
        print("2. Verify username and password")
        print("3. Check network access (IP whitelist)")
        print("4. Ensure cluster is running")
        return False

def migrate_data_to_atlas():
    """Migrate data from local to Atlas."""
    try:
        print("\n🚀 Migrating data to Atlas...")
        
        # Connect to local MongoDB
        local_client = pymongo.MongoClient('mongodb://localhost:27017/')
        local_db = local_client['olaf_backend']
        
        # Connect to Atlas
        from dotenv import load_dotenv
        load_dotenv()
        
        atlas_uri = os.environ.get('MONGODB_ATLAS_URI', '')
        atlas_client = pymongo.MongoClient(atlas_uri)
        atlas_db = atlas_client['olaf_backend']
        
        # Get collections from local
        collections = local_db.list_collection_names()
        
        for collection_name in collections:
            print(f"📦 Migrating {collection_name}...")
            
            # Get all documents from local
            local_collection = local_db[collection_name]
            documents = list(local_collection.find())
            
            if documents:
                # Clear existing data in Atlas
                atlas_collection = atlas_db[collection_name]
                atlas_collection.drop()
                
                # Insert into Atlas
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

if __name__ == "__main__":
    import pymongo
    
    print("🌐 MongoDB Atlas Setup")
    print("=" * 50)
    print("1. Update Atlas configuration")
    print("2. Test Atlas connection")
    print("3. Migrate data to Atlas")
    print("4. Exit")
    print()
    
    while True:
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == '1':
            update_env_file()
        elif choice == '2':
            test_atlas_connection()
        elif choice == '3':
            migrate_data_to_atlas()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        print("\n" + "="*50 + "\n")
