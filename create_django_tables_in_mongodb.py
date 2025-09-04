#!/usr/bin/env python3
"""
Create MongoDB collections based on Django models structure.
"""
import pymongo
from datetime import datetime
import os
from dotenv import load_dotenv

def create_mongodb_collections():
    """Create MongoDB collections based on Django models."""
    print("🗄️ Creating MongoDB Collections from Django Models")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Connect to local MongoDB
        print("📦 Connecting to local MongoDB...")
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['olaf_backend']
        
        # Clear existing collections
        print("🧹 Clearing existing collections...")
        collections_to_clear = ['authentication_account', 'blog_post', 'blog_comment', 'blog_postlike', 'blog_commentlike']
        for collection_name in collections_to_clear:
            if collection_name in db.list_collection_names():
                db[collection_name].drop()
                print(f"  ✅ Cleared {collection_name}")
        
        print("\n📚 Creating collections based on Django models...")
        
        # 1. Create authentication_account collection
        print("\n👤 Creating authentication_account collection...")
        account_collection = db['authentication_account']
        
        # Create indexes for authentication_account
        account_collection.create_index("email", unique=True)
        account_collection.create_index("username", unique=True)
        account_collection.create_index("created_at")
        account_collection.create_index([("email", 1), ("username", 1)])
        
        # Insert sample accounts
        sample_accounts = [
            {
                "id": 1,
                "email": "admin@example.com",
                "username": "admin",
                "first_name": "Admin",
                "last_name": "User",
                "phone": "0812345678",
                "is_admin": True,
                "is_active": True,
                "is_staff": True,
                "is_superuser": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "password": "pbkdf2_sha256$260000$...",  # Hashed password
                "last_login": None
            },
            {
                "id": 2,
                "email": "user@example.com",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "phone": "0812345679",
                "is_admin": False,
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "password": "pbkdf2_sha256$260000$...",  # Hashed password
                "last_login": None
            }
        ]
        
        account_collection.insert_many(sample_accounts)
        print(f"  ✅ Created {len(sample_accounts)} accounts")
        
        # 2. Create blog_post collection
        print("\n📝 Creating blog_post collection...")
        post_collection = db['blog_post']
        
        # Create indexes for blog_post
        post_collection.create_index("post_id", unique=True)
        post_collection.create_index("user_id")
        post_collection.create_index("post_datetime")
        post_collection.create_index([("header", "text"), ("post_text", "text")])
        
        # Insert sample posts
        sample_posts = [
            {
                "post_id": 1,
                "header": "Welcome to Our Blog",
                "short": "First blog post",
                "post_text": "This is the first post on our blog. Welcome everyone! This is a longer content to demonstrate the blog functionality.",
                "post_datetime": datetime.now(),
                "user_id": 1,  # admin user
                "image": "posts/images/welcome.jpg"
            },
            {
                "post_id": 2,
                "header": "MongoDB Integration",
                "short": "Database setup",
                "post_text": "We have successfully integrated MongoDB with our Django application. This allows for better scalability and performance.",
                "post_datetime": datetime.now(),
                "user_id": 1,  # admin user
                "image": "posts/images/mongodb.jpg"
            },
            {
                "post_id": 3,
                "header": "Django REST Framework",
                "short": "API development",
                "post_text": "Using Django REST Framework to create powerful APIs for our application. This makes it easy to build frontend applications.",
                "post_datetime": datetime.now(),
                "user_id": 2,  # test user
                "image": None
            }
        ]
        
        post_collection.insert_many(sample_posts)
        print(f"  ✅ Created {len(sample_posts)} posts")
        
        # 3. Create blog_comment collection
        print("\n💬 Creating blog_comment collection...")
        comment_collection = db['blog_comment']
        
        # Create indexes for blog_comment
        comment_collection.create_index("comment_id", unique=True)
        comment_collection.create_index("post_id")
        comment_collection.create_index("user_id")
        comment_collection.create_index("comment_datetime")
        
        # Insert sample comments
        sample_comments = [
            {
                "comment_id": 1,
                "post_id": 1,
                "user_id": 2,
                "comment_datetime": datetime.now(),
                "comment_text": "Great first post! Looking forward to more content."
            },
            {
                "comment_id": 2,
                "post_id": 1,
                "user_id": 1,
                "comment_datetime": datetime.now(),
                "comment_text": "Thank you for the feedback!"
            },
            {
                "comment_id": 3,
                "post_id": 2,
                "user_id": 2,
                "comment_datetime": datetime.now(),
                "comment_text": "MongoDB is indeed a great choice for this project."
            }
        ]
        
        comment_collection.insert_many(sample_comments)
        print(f"  ✅ Created {len(sample_comments)} comments")
        
        # 4. Create blog_postlike collection
        print("\n❤️ Creating blog_postlike collection...")
        postlike_collection = db['blog_postlike']
        
        # Create indexes for blog_postlike
        postlike_collection.create_index([("post_id", 1), ("user_id", 1)], unique=True)
        postlike_collection.create_index("post_id")
        postlike_collection.create_index("user_id")
        
        # Insert sample post likes
        sample_post_likes = [
            {"post_id": 1, "user_id": 2},
            {"post_id": 2, "user_id": 1},
            {"post_id": 2, "user_id": 2},
            {"post_id": 3, "user_id": 1}
        ]
        
        postlike_collection.insert_many(sample_post_likes)
        print(f"  ✅ Created {len(sample_post_likes)} post likes")
        
        # 5. Create blog_commentlike collection
        print("\n👍 Creating blog_commentlike collection...")
        commentlike_collection = db['blog_commentlike']
        
        # Create indexes for blog_commentlike
        commentlike_collection.create_index([("comment_id", 1), ("user_id", 1)], unique=True)
        commentlike_collection.create_index("comment_id")
        commentlike_collection.create_index("user_id")
        
        # Insert sample comment likes
        sample_comment_likes = [
            {"comment_id": 1, "user_id": 1},
            {"comment_id": 2, "user_id": 2},
            {"comment_id": 3, "user_id": 1}
        ]
        
        commentlike_collection.insert_many(sample_comment_likes)
        print(f"  ✅ Created {len(sample_comment_likes)} comment likes")
        
        # Show final statistics
        print("\n📊 Final Database Statistics:")
        print("-" * 40)
        
        collections = ['authentication_account', 'blog_post', 'blog_comment', 'blog_postlike', 'blog_commentlike']
        for collection_name in collections:
            count = db[collection_name].count_documents({})
            print(f"  {collection_name}: {count} documents")
        
        # Show total stats
        stats = db.command("dbStats")
        print(f"\n📈 Total Documents: {stats['objects']}")
        print(f"💾 Data Size: {stats['dataSize']:,} bytes")
        print(f"🗂️ Storage Size: {stats['storageSize']:,} bytes")
        print(f"📈 Total Indexes: {stats['indexes']}")
        
        client.close()
        print("\n✅ MongoDB collections created successfully!")
        print("🎉 Your Django tables are now available in MongoDB!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating collections: {e}")
        return False

def show_sample_data():
    """Show sample data from collections."""
    print("\n🔍 Sample Data Preview:")
    print("=" * 60)
    
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['olaf_backend']
        
        # Show accounts
        print("\n👤 Accounts:")
        accounts = list(db['authentication_account'].find().limit(2))
        for account in accounts:
            print(f"  - {account['username']} ({account['email']}) - {account['first_name']} {account['last_name']}")
        
        # Show posts
        print("\n📝 Posts:")
        posts = list(db['blog_post'].find().limit(3))
        for post in posts:
            print(f"  - {post['header']} by user_id {post['user_id']}")
        
        # Show comments
        print("\n💬 Comments:")
        comments = list(db['blog_comment'].find().limit(3))
        for comment in comments:
            print(f"  - Comment on post_id {comment['post_id']} by user_id {comment['user_id']}")
        
        # Show likes
        print("\n❤️ Post Likes:")
        post_likes = list(db['blog_postlike'].find().limit(3))
        for like in post_likes:
            print(f"  - User {like['user_id']} likes post {like['post_id']}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error showing sample data: {e}")

if __name__ == "__main__":
    if create_mongodb_collections():
        show_sample_data()
