#!/usr/bin/env python3
"""
Simple script to migrate data from local MongoDB to Atlas.
"""
import pymongo
import os
from dotenv import load_dotenv

def migrate_to_atlas():
    """Migrate data from local MongoDB to Atlas."""
    print("🚀 Migrating data to MongoDB Atlas...")
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Connect to local MongoDB
        print("📦 Connecting to local MongoDB...")
        local_client = pymongo.MongoClient('mongodb://localhost:27017/')
        local_db = local_client['olaf_backend']
        
        # Connect to Atlas
        print("🌐 Connecting to Atlas...")
        atlas_uri = os.environ.get('MONGODB_ATLAS_URI', '')
        if not atlas_uri or 'username:password@cluster.mongodb.net' in atlas_uri:
            print("❌ Please update MONGODB_ATLAS_URI in .env file first!")
            return False
        
        atlas_client = pymongo.MongoClient(atlas_uri)
        atlas_db = atlas_client['olaf_backend']
        
        # Test Atlas connection
        atlas_client.admin.command('ping')
        print("✅ Connected to Atlas successfully!")
        
        # Get collections from local
        collections = local_db.list_collection_names()
        print(f"📚 Found collections: {collections}")
        
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
        
        # Show Atlas stats
        print("\n📊 Atlas Database Stats:")
        stats = atlas_db.command("dbStats")
        print(f"  Documents: {stats['objects']}")
        print(f"  Collections: {stats['collections']}")
        print(f"  Data Size: {stats['dataSize']:,} bytes")
        
        local_client.close()
        atlas_client.close()
        
        print("\n✅ Migration completed successfully!")
        print("🌐 You can now view your data in MongoDB Atlas!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    migrate_to_atlas()
