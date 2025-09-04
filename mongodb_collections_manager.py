#!/usr/bin/env python3
"""
MongoDB Collections Manager
สคริปต์สำหรับจัดการ Collections (Tables) ใน MongoDB
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.development')
django.setup()

from utils.mongodb import get_client, get_database


class MongoDBCollectionsManager:
    """จัดการ Collections ใน MongoDB"""
    
    def __init__(self):
        self.client = get_client()
        self.db = get_database()
    
    def list_collections(self):
        """แสดงรายการ Collections ทั้งหมด"""
        print("📊 MongoDB Collections:")
        print("=" * 50)
        
        collections = self.db.list_collection_names()
        if not collections:
            print("❌ ไม่มี Collections ในฐานข้อมูล")
            return
        
        for i, collection in enumerate(collections, 1):
            count = self.db[collection].count_documents({})
            print(f"{i:2d}. {collection:<25} ({count:>3} documents)")
    
    def create_collection(self, name, options=None):
        """สร้าง Collection ใหม่"""
        try:
            if options:
                self.db.create_collection(name, **options)
            else:
                self.db.create_collection(name)
            print(f"✅ สร้าง Collection '{name}' เรียบร้อย")
            return True
        except Exception as e:
            if "already exists" in str(e):
                print(f"⚠️ Collection '{name}' มีอยู่แล้ว")
            else:
                print(f"❌ เกิดข้อผิดพลาด: {e}")
            return False
    
    def drop_collection(self, name):
        """ลบ Collection"""
        try:
            self.db.drop_collection(name)
            print(f"✅ ลบ Collection '{name}' เรียบร้อย")
            return True
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            return False
    
    def create_sample_data(self):
        """สร้างข้อมูลตัวอย่างใน Collections"""
        print("\n🎯 กำลังสร้างข้อมูลตัวอย่าง...")
        
        # สร้างข้อมูล Users
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_active': True,
                'is_staff': True,
                'created_at': datetime.now().isoformat()
            },
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_active': True,
                'is_staff': False,
                'created_at': datetime.now().isoformat()
            }
        ]
        
        users_collection = self.db['users']
        for user in users_data:
            existing = users_collection.find_one({'username': user['username']})
            if not existing:
                users_collection.insert_one(user)
                print(f"✅ สร้าง User: {user['username']}")
        
        # สร้างข้อมูล Posts
        posts_data = [
            {
                'title': 'Welcome to MongoDB!',
                'content': 'This is our first post using MongoDB. MongoDB is a NoSQL database that stores data in flexible, JSON-like documents.',
                'author': 'admin',
                'tags': ['mongodb', 'database', 'nosql'],
                'created_at': datetime.now().isoformat(),
                'likes': 5,
                'comments': []
            },
            {
                'title': 'Django with MongoDB',
                'content': 'Learn how to integrate Django with MongoDB using MongoEngine. This allows you to use MongoDB as your primary database.',
                'author': 'john_doe',
                'tags': ['django', 'mongodb', 'python'],
                'created_at': datetime.now().isoformat(),
                'likes': 3,
                'comments': []
            }
        ]
        
        posts_collection = self.db['posts']
        for post in posts_data:
            existing = posts_collection.find_one({'title': post['title']})
            if not existing:
                posts_collection.insert_one(post)
                print(f"✅ สร้าง Post: {post['title']}")
        
        # สร้างข้อมูล Comments
        comments_data = [
            {
                'post_title': 'Welcome to MongoDB!',
                'author': 'john_doe',
                'content': 'Great post! MongoDB is really powerful.',
                'created_at': datetime.now().isoformat(),
                'likes': 2
            },
            {
                'post_title': 'Django with MongoDB',
                'author': 'admin',
                'content': 'Thanks for sharing this tutorial!',
                'created_at': datetime.now().isoformat(),
                'likes': 1
            }
        ]
        
        comments_collection = self.db['comments']
        for comment in comments_data:
            existing = comments_collection.find_one({
                'post_title': comment['post_title'],
                'author': comment['author']
            })
            if not existing:
                comments_collection.insert_one(comment)
                print(f"✅ สร้าง Comment: {comment['author']} on {comment['post_title']}")
    
    def show_collection_stats(self):
        """แสดงสถิติของ Collections"""
        print("\n📊 สถิติ Collections:")
        print("=" * 50)
        
        collections = self.db.list_collection_names()
        total_docs = 0
        
        for collection in collections:
            count = self.db[collection].count_documents({})
            total_docs += count
            print(f"{collection:<25}: {count:>5} documents")
        
        print("-" * 50)
        print(f"{'Total':<25}: {total_docs:>5} documents")
    
    def create_indexes(self):
        """สร้าง Indexes สำหรับ Collections"""
        print("\n🔧 กำลังสร้าง Indexes...")
        
        # Indexes สำหรับ Users
        users_collection = self.db['users']
        users_indexes = [
            [('username', 1)],
            [('email', 1)],
            [('created_at', -1)]
        ]
        
        for index in users_indexes:
            try:
                users_collection.create_index(index, background=True)
                print(f"✅ สร้าง Index สำหรับ users: {index}")
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"⚠️ Index users: {e}")
        
        # Indexes สำหรับ Posts
        posts_collection = self.db['posts']
        posts_indexes = [
            [('author', 1)],
            [('created_at', -1)],
            [('tags', 1)],
            [('title', 'text'), ('content', 'text')]  # Text search index
        ]
        
        for index in posts_indexes:
            try:
                posts_collection.create_index(index, background=True)
                print(f"✅ สร้าง Index สำหรับ posts: {index}")
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"⚠️ Index posts: {e}")
        
        # Indexes สำหรับ Comments
        comments_collection = self.db['comments']
        comments_indexes = [
            [('post_title', 1)],
            [('author', 1)],
            [('created_at', -1)]
        ]
        
        for index in comments_indexes:
            try:
                comments_collection.create_index(index, background=True)
                print(f"✅ สร้าง Index สำหรับ comments: {index}")
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"⚠️ Index comments: {e}")
    
    def search_posts(self, query):
        """ค้นหา Posts"""
        posts_collection = self.db['posts']
        
        # Text search
        results = posts_collection.find(
            {'$text': {'$search': query}},
            {'score': {'$meta': 'textScore'}}
        ).sort([('score', {'$meta': 'textScore'})])
        
        print(f"\n🔍 ผลการค้นหา '{query}':")
        print("=" * 50)
        
        count = 0
        for post in results:
            count += 1
            print(f"{count}. {post['title']}")
            print(f"   Author: {post['author']}")
            print(f"   Tags: {', '.join(post['tags'])}")
            print(f"   Likes: {post['likes']}")
            print()
        
        if count == 0:
            print("❌ ไม่พบผลการค้นหา")
    
    def interactive_mode(self):
        """โหมด Interactive"""
        print("\n🎮 โหมด Interactive - MongoDB Collections Manager")
        print("=" * 60)
        
        while True:
            print("\nเลือกคำสั่ง:")
            print("1. แสดง Collections ทั้งหมด")
            print("2. สร้าง Collection ใหม่")
            print("3. ลบ Collection")
            print("4. สร้างข้อมูลตัวอย่าง")
            print("5. แสดงสถิติ")
            print("6. สร้าง Indexes")
            print("7. ค้นหา Posts")
            print("8. ออกจากโปรแกรม")
            
            choice = input("\nกรุณาเลือก (1-8): ").strip()
            
            if choice == '1':
                self.list_collections()
            elif choice == '2':
                name = input("ชื่อ Collection: ").strip()
                if name:
                    self.create_collection(name)
            elif choice == '3':
                name = input("ชื่อ Collection ที่จะลบ: ").strip()
                if name:
                    confirm = input(f"ยืนยันการลบ '{name}'? (y/N): ").strip().lower()
                    if confirm == 'y':
                        self.drop_collection(name)
            elif choice == '4':
                self.create_sample_data()
            elif choice == '5':
                self.show_collection_stats()
            elif choice == '6':
                self.create_indexes()
            elif choice == '7':
                query = input("คำค้นหา: ").strip()
                if query:
                    self.search_posts(query)
            elif choice == '8':
                print("👋 ขอบคุณที่ใช้งาน!")
                break
            else:
                print("❌ กรุณาเลือกตัวเลข 1-8")


def main():
    """ฟังก์ชันหลัก"""
    print("🚀 MongoDB Collections Manager")
    print("=" * 40)
    
    try:
        manager = MongoDBCollectionsManager()
        
        # ตรวจสอบการเชื่อมต่อ
        manager.client.admin.command('ping')
        print("✅ เชื่อมต่อ MongoDB สำเร็จ!")
        
        # รันโหมด Interactive
        manager.interactive_mode()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
