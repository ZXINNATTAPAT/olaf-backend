#!/usr/bin/env python3
"""
Script to check MongoDB collections and data.
"""
import pymongo
from pprint import pprint
import json
from datetime import datetime

def check_mongodb():
    """Check MongoDB collections and display data."""
    try:
        # Connect to local MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['olaf_backend']
        
        print("🔍 MongoDB Database Status")
        print("=" * 50)
        
        # Database stats
        stats = db.command("dbStats")
        print(f"📊 Database: {stats['db']}")
        print(f"📁 Collections: {stats['collections']}")
        print(f"📄 Documents: {stats['objects']}")
        print(f"💾 Data Size: {stats['dataSize']:,} bytes")
        print(f"🗂️  Storage Size: {stats['storageSize']:,} bytes")
        print(f"📈 Indexes: {stats['indexes']}")
        print(f"🔍 Index Size: {stats['indexSize']:,} bytes")
        print()
        
        # List all collections
        collections = db.list_collection_names()
        print("📚 Available Collections:")
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"  - {collection_name}: {count} documents")
        print()
        
        # Show sample data from each collection
        for collection_name in collections:
            collection = db[collection_name]
            print(f"📋 Sample data from {collection_name}:")
            print("-" * 40)
            
            # Get first 3 documents
            docs = list(collection.find().limit(3))
            for i, doc in enumerate(docs, 1):
                print(f"Document {i}:")
                # Convert ObjectId and datetime to string for display
                doc_display = {}
                for key, value in doc.items():
                    if hasattr(value, 'isoformat'):  # datetime
                        doc_display[key] = value.isoformat()
                    elif hasattr(value, '__str__'):  # ObjectId and others
                        doc_display[key] = str(value)
                    else:
                        doc_display[key] = value
                
                pprint(doc_display, width=80, depth=2)
                print()
        
        # Show indexes for each collection
        print("🔍 Indexes Information:")
        print("-" * 40)
        for collection_name in collections:
            collection = db[collection_name]
            indexes = list(collection.list_indexes())
            print(f"\n{collection_name}:")
            for index in indexes:
                print(f"  - {index['name']}: {index['key']}")
        
        client.close()
        print("\n✅ MongoDB check completed successfully!")
        
    except Exception as e:
        print(f"❌ Error checking MongoDB: {e}")

if __name__ == "__main__":
    check_mongodb()
