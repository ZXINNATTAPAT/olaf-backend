# 📊 คู่มือการจัดการ MongoDB Collections (Tables)

## 🎯 ภาพรวม

MongoDB ใช้ **Collections** แทน **Tables** ใน SQL Database
- **SQL**: Tables → Rows → Columns
- **MongoDB**: Collections → Documents → Fields

## 🚀 วิธีการใช้งาน

### 1. รันสคริปต์จัดการ Collections

```bash
python3 mongodb_collections_manager.py
```

### 2. คำสั่งพื้นฐาน

#### แสดง Collections ทั้งหมด
```python
from utils.mongodb import get_database

db = get_database()
collections = db.list_collection_names()
print(collections)
```

#### สร้าง Collection ใหม่
```python
# สร้าง Collection เปล่า
db.create_collection('my_collection')

# สร้าง Collection พร้อม options
db.create_collection('capped_collection', {
    'capped': True,
    'size': 1000000,  # 1MB
    'max': 1000       # 1000 documents
})
```

#### ลบ Collection
```python
db.drop_collection('my_collection')
```

## 📋 Collections ที่แนะนำสำหรับแอปพลิเคชัน

### 1. **users** - ข้อมูลผู้ใช้
```json
{
  "_id": ObjectId("..."),
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_staff": false,
  "created_at": "2025-09-03T10:09:14Z",
  "last_login": "2025-09-03T10:09:14Z"
}
```

### 2. **posts** - โพสต์บล็อก
```json
{
  "_id": ObjectId("..."),
  "title": "Welcome to MongoDB!",
  "content": "This is our first post...",
  "author": "john_doe",
  "tags": ["mongodb", "database", "tutorial"],
  "created_at": "2025-09-03T10:09:14Z",
  "updated_at": "2025-09-03T10:09:14Z",
  "likes": 5,
  "views": 100,
  "status": "published"
}
```

### 3. **comments** - ความคิดเห็น
```json
{
  "_id": ObjectId("..."),
  "post_id": ObjectId("..."),
  "author": "jane_doe",
  "content": "Great post!",
  "created_at": "2025-09-03T10:09:14Z",
  "likes": 2,
  "parent_id": null
}
```

### 4. **sessions** - เซสชันผู้ใช้
```json
{
  "_id": ObjectId("..."),
  "session_key": "abc123...",
  "user_id": ObjectId("..."),
  "data": {...},
  "expire_date": "2025-09-10T10:09:14Z"
}
```

### 5. **cache** - ข้อมูลแคช
```json
{
  "_id": ObjectId("..."),
  "key": "user:123:profile",
  "value": {...},
  "expires_at": "2025-09-03T11:09:14Z"
}
```

### 6. **logs** - ระบบล็อก
```json
{
  "_id": ObjectId("..."),
  "level": "INFO",
  "message": "User logged in",
  "user_id": ObjectId("..."),
  "ip_address": "192.168.1.1",
  "created_at": "2025-09-03T10:09:14Z"
}
```

## 🔧 การสร้าง Indexes

### Indexes ที่แนะนำ

#### Users Collection
```python
# Username index (unique)
users.create_index([('username', 1)], unique=True)

# Email index (unique)
users.create_index([('email', 1)], unique=True)

# Created date index
users.create_index([('created_at', -1)])

# Compound index
users.create_index([('is_active', 1), ('created_at', -1)])
```

#### Posts Collection
```python
# Author index
posts.create_index([('author', 1)])

# Created date index
posts.create_index([('created_at', -1)])

# Tags index
posts.create_index([('tags', 1)])

# Text search index
posts.create_index([('title', 'text'), ('content', 'text')])

# Status and date compound index
posts.create_index([('status', 1), ('created_at', -1)])
```

#### Comments Collection
```python
# Post ID index
comments.create_index([('post_id', 1)])

# Author index
comments.create_index([('author', 1)])

# Created date index
comments.create_index([('created_at', -1)])

# Post and date compound index
comments.create_index([('post_id', 1), ('created_at', -1)])
```

## 🔍 การค้นหาข้อมูล

### Text Search
```python
# ค้นหาใน title และ content
results = posts.find({
    '$text': {'$search': 'mongodb tutorial'}
}).sort([('score', {'$meta': 'textScore'})])
```

### Query ตัวอย่าง
```python
# ค้นหา posts ของ author
posts.find({'author': 'john_doe'})

# ค้นหา posts ที่มี tag
posts.find({'tags': 'mongodb'})

# ค้นหา posts ที่สร้างใน 7 วันที่ผ่านมา
from datetime import datetime, timedelta
week_ago = datetime.now() - timedelta(days=7)
posts.find({'created_at': {'$gte': week_ago}})

# ค้นหา posts ที่มี likes มากกว่า 10
posts.find({'likes': {'$gt': 10}})
```

## 📊 การจัดการข้อมูล

### การแทรกข้อมูล
```python
# แทรก document เดียว
result = collection.insert_one({
    'name': 'John Doe',
    'email': 'john@example.com'
})

# แทรกหลาย documents
result = collection.insert_many([
    {'name': 'John', 'age': 30},
    {'name': 'Jane', 'age': 25}
])
```

### การอัปเดตข้อมูล
```python
# อัปเดต document เดียว
collection.update_one(
    {'username': 'john_doe'},
    {'$set': {'last_login': datetime.now()}}
)

# อัปเดตหลาย documents
collection.update_many(
    {'status': 'draft'},
    {'$set': {'status': 'published'}}
)
```

### การลบข้อมูล
```python
# ลบ document เดียว
collection.delete_one({'username': 'john_doe'})

# ลบหลาย documents
collection.delete_many({'status': 'deleted'})
```

## 🎮 การใช้งานสคริปต์จัดการ

### รันสคริปต์
```bash
python3 mongodb_collections_manager.py
```

### เมนูที่ใช้ได้
1. **แสดง Collections ทั้งหมด** - ดูรายการ Collections และจำนวน documents
2. **สร้าง Collection ใหม่** - สร้าง Collection เปล่า
3. **ลบ Collection** - ลบ Collection และข้อมูลทั้งหมด
4. **สร้างข้อมูลตัวอย่าง** - สร้างข้อมูลทดสอบ
5. **แสดงสถิติ** - ดูสถิติของ Collections
6. **สร้าง Indexes** - สร้าง indexes สำหรับ performance
7. **ค้นหา Posts** - ค้นหาข้อมูลใน posts collection
8. **ออกจากโปรแกรม** - ปิดโปรแกรม

## ⚡ Tips สำหรับ Performance

### 1. ใช้ Indexes
- สร้าง indexes สำหรับ fields ที่ใช้ค้นหาบ่อย
- ใช้ compound indexes สำหรับ queries ที่ซับซ้อน

### 2. ใช้ Projection
```python
# ดึงเฉพาะ fields ที่ต้องการ
posts.find({}, {'title': 1, 'author': 1, 'created_at': 1})
```

### 3. ใช้ Limit และ Skip
```python
# จำกัดจำนวนผลลัพธ์
posts.find().limit(10).skip(20)
```

### 4. ใช้ Aggregation Pipeline
```python
# นับจำนวน posts ของแต่ละ author
posts.aggregate([
    {'$group': {'_id': '$author', 'count': {'$sum': 1}}},
    {'$sort': {'count': -1}}
])
```

## 🛠️ การแก้ไขปัญหา

### 1. Connection Error
```bash
# ตรวจสอบ MongoDB service
brew services list | grep mongodb

# เริ่ม MongoDB service
brew services start mongodb-community
```

### 2. Permission Error
```bash
# ตรวจสอบ permissions
ls -la /usr/local/var/mongodb/

# แก้ไข permissions
sudo chown -R $(whoami) /usr/local/var/mongodb/
```

### 3. Index Error
```python
# ตรวจสอบ indexes ที่มีอยู่
collection.list_indexes()

# ลบ index ที่ไม่ต้องการ
collection.drop_index('index_name')
```

## 📚 เอกสารเพิ่มเติม

- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)

---

**หมายเหตุ**: Collections ใน MongoDB จะถูกสร้างอัตโนมัติเมื่อมีการแทรกข้อมูลครั้งแรก ไม่จำเป็นต้องสร้างล่วงหน้าเหมือน SQL Tables
