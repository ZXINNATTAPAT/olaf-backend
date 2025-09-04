# 🗄️ MongoDB Management Commands Guide

## 📋 **คำสั่งทั้งหมดสำหรับควบคุมดูแล MongoDB**

### 🔧 **1. Django Management Commands**

#### **MongoDB Setup & Optimization**
```bash
# ดู help
DJANGO_SETTINGS_MODULE=mysite.settings.development python3 manage.py mongodb_setup --help

# สร้าง indexes
DJANGO_SETTINGS_MODULE=mysite.settings.development python3 manage.py mongodb_setup --create-indexes

# ดูสถิติ
DJANGO_SETTINGS_MODULE=mysite.settings.development python3 manage.py mongodb_setup --stats

# Optimize collections
DJANGO_SETTINGS_MODULE=mysite.settings.development python3 manage.py mongodb_setup --optimize

# รันทุกอย่าง
DJANGO_SETTINGS_MODULE=mysite.settings.development python3 manage.py mongodb_setup --all
```

#### **Create MongoDB Collections**
```bash
# สร้าง collections และข้อมูลตัวอย่าง
DJANGO_SETTINGS_MODULE=mysite.settings.development python3 manage.py create_mongodb_collections --sample-data

# สร้าง collections อย่างเดียว
DJANGO_SETTINGS_MODULE=mysite.settings.development python3 manage.py create_mongodb_collections --collections-only
```

### 🐍 **2. Python Scripts**

#### **ตรวจสอบข้อมูล MongoDB**
```bash
# ดูข้อมูลทั้งหมดใน MongoDB
python3 check_mongodb.py

# สร้างข้อมูลตาม Django models
python3 create_django_tables_in_mongodb.py

# ตั้งค่า Atlas
python3 setup_atlas.py

# อัปเดตการตั้งค่า
python3 update_env.py

# ย้ายข้อมูลไป Atlas
python3 migrate_to_atlas.py
```

### 🖥️ **3. MongoDB Shell Commands**

#### **การเชื่อมต่อ**
```bash
# เชื่อมต่อ MongoDB
mongosh

# เชื่อมต่อ database เฉพาะ
mongosh olaf_backend

# เชื่อมต่อและรันคำสั่ง
mongosh olaf_backend --eval "db.stats()"
```

#### **ดูข้อมูล**
```bash
# ดู databases
mongosh --eval "show dbs"

# ดู collections
mongosh olaf_backend --eval "show collections"

# ดูข้อมูลใน collection
mongosh olaf_backend --eval "db.authentication_account.find().pretty()"
mongosh olaf_backend --eval "db.blog_post.find().pretty()"
mongosh olaf_backend --eval "db.blog_comment.find().pretty()"
mongosh olaf_backend --eval "db.blog_postlike.find().pretty()"
mongosh olaf_backend --eval "db.blog_commentlike.find().pretty()"
```

#### **ค้นหาข้อมูล**
```bash
# ค้นหาผู้ใช้
mongosh olaf_backend --eval "db.authentication_account.find({username: 'admin'}).pretty()"

# ค้นหา posts
mongosh olaf_backend --eval "db.blog_post.find({user_id: 1}).pretty()"

# ค้นหาด้วย regex
mongosh olaf_backend --eval "db.blog_post.find({header: /MongoDB/}).pretty()"

# นับจำนวนเอกสาร
mongosh olaf_backend --eval "db.authentication_account.countDocuments({})"
mongosh olaf_backend --eval "db.blog_post.countDocuments({})"
```

#### **แก้ไขข้อมูล**
```bash
# เพิ่มข้อมูลใหม่
mongosh olaf_backend --eval "db.authentication_account.insertOne({id: 3, email: 'new@example.com', username: 'newuser', first_name: 'New', last_name: 'User', phone: '0812345670', is_admin: false, is_active: true, is_staff: false, is_superuser: false, created_at: new Date(), updated_at: new Date()})"

# อัปเดตข้อมูล
mongosh olaf_backend --eval "db.authentication_account.updateOne({username: 'admin'}, {\$set: {last_login: new Date()}})"

# ลบข้อมูล
mongosh olaf_backend --eval "db.authentication_account.deleteOne({username: 'newuser'})"
```

#### **Indexes**
```bash
# ดู indexes
mongosh olaf_backend --eval "db.authentication_account.getIndexes()"
mongosh olaf_backend --eval "db.blog_post.getIndexes()"

# สร้าง index ใหม่
mongosh olaf_backend --eval "db.authentication_account.createIndex({email: 1})"
mongosh olaf_backend --eval "db.blog_post.createIndex({post_datetime: -1})"

# ลบ index
mongosh olaf_backend --eval "db.authentication_account.dropIndex({email: 1})"
```

### 🔍 **4. Database Statistics**

#### **สถิติทั่วไป**
```bash
# สถิติ database
mongosh olaf_backend --eval "db.stats()"

# สถิติ collection
mongosh olaf_backend --eval "db.authentication_account.stats()"
mongosh olaf_backend --eval "db.blog_post.stats()"

# ดูขนาดข้อมูล
mongosh olaf_backend --eval "db.runCommand({collStats: 'authentication_account'})"
```

#### **Performance Monitoring**
```bash
# ดูการใช้งาน
mongosh olaf_backend --eval "db.runCommand({serverStatus: 1})"

# ดู connections
mongosh olaf_backend --eval "db.runCommand({connPoolStats: 1})"

# ดู operations
mongosh olaf_backend --eval "db.runCommand({currentOp: 1})"
```

### 🛠️ **5. Maintenance Commands**

#### **Backup & Restore**
```bash
# Backup database
mongodump --db olaf_backend --out ./backup/

# Restore database
mongorestore --db olaf_backend ./backup/olaf_backend/

# Backup collection เฉพาะ
mongodump --db olaf_backend --collection authentication_account --out ./backup/
```

#### **Cleanup**
```bash
# ลบ collection ทั้งหมด
mongosh olaf_backend --eval "db.authentication_account.drop()"
mongosh olaf_backend --eval "db.blog_post.drop()"

# ลบ database ทั้งหมด
mongosh --eval "db.dropDatabase()" olaf_backend

# ลบข้อมูลเก่า (เก่ากว่า 30 วัน)
mongosh olaf_backend --eval "db.blog_post.deleteMany({post_datetime: {\$lt: new Date(Date.now() - 30*24*60*60*1000)}})"
```

### 🔧 **6. Service Management**

#### **MongoDB Service**
```bash
# เริ่ม MongoDB
brew services start mongodb/brew/mongodb-community

# หยุด MongoDB
brew services stop mongodb/brew/mongodb-community

# รีสตาร์ท MongoDB
brew services restart mongodb/brew/mongodb-community

# ดูสถานะ
brew services list | grep mongodb
```

#### **Django Server**
```bash
# เริ่ม Django server
DJANGO_SETTINGS_MODULE=mysite.settings.development python3 manage.py runserver

# เริ่ม Django server พร้อม MongoDB
DJANGO_SETTINGS_MODULE=mysite.settings.development python3 manage.py runserver 8000
```

### 📊 **7. Monitoring & Debugging**

#### **Logs**
```bash
# ดู MongoDB logs
tail -f /opt/homebrew/var/log/mongodb/mongo.log

# ดู Django logs
tail -f logs/django.log
```

#### **Debug Commands**
```bash
# ตรวจสอบการเชื่อมต่อ
mongosh --eval "db.runCommand('ping')"

# ตรวจสอบ authentication
mongosh olaf_backend --eval "db.runCommand({usersInfo: 1})"

# ตรวจสอบ indexes
mongosh olaf_backend --eval "db.authentication_account.explain().find({email: 'admin@example.com'})"
```

### 🌐 **8. Atlas Commands**

#### **Atlas Management**
```bash
# ตั้งค่า Atlas
python3 update_env.py

# ทดสอบ Atlas
python3 setup_atlas.py

# ย้ายข้อมูลไป Atlas
python3 migrate_to_atlas.py
```

#### **Atlas Connection**
```bash
# เชื่อมต่อ Atlas (ต้องตั้งค่า .env ก่อน)
mongosh "mongodb+srv://username:password@cluster.mongodb.net/olaf_backend"

# ดูข้อมูลใน Atlas
mongosh "mongodb+srv://username:password@cluster.mongodb.net/olaf_backend" --eval "db.stats()"
```

### 🚀 **9. Quick Commands**

#### **Daily Operations**
```bash
# ตรวจสอบสถานะ
python3 check_mongodb.py

# รัน optimization
DJANGO_SETTINGS_MODULE=mysite.settings.development python3 manage.py mongodb_setup --all

# ดูข้อมูลล่าสุด
mongosh olaf_backend --eval "db.blog_post.find().sort({post_datetime: -1}).limit(5).pretty()"
```

#### **Emergency Commands**
```bash
# รีสตาร์ททุกอย่าง
brew services restart mongodb/brew/mongodb-community
DJANGO_SETTINGS_MODULE=mysite.settings.development python3 manage.py mongodb_setup --all

# ลบข้อมูลทั้งหมดและเริ่มใหม่
mongosh olaf_backend --eval "db.dropDatabase()"
python3 create_django_tables_in_mongodb.py
```

---

## 📝 **หมายเหตุ**

- ใช้ `DJANGO_SETTINGS_MODULE=mysite.settings.development` สำหรับ development
- ใช้ `DJANGO_SETTINGS_MODULE=mysite.settings.production` สำหรับ production
- ตรวจสอบ `.env` file ก่อนใช้ Atlas commands
- ใช้ `mongosh` แทน `mongo` (deprecated)

## 🔗 **Useful Links**

- [MongoDB Documentation](https://docs.mongodb.com/)
- [MongoDB Atlas](https://www.mongodb.com/atlas)
- [Django MongoDB Integration](https://docs.djangoproject.com/)
