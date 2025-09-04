# 🔧 คู่มือแก้ไขปัญหา Redis Connection

## ❌ ปัญหาที่พบ
```
ConnectionError at /admin/login/
Error 61 connecting to 127.0.0.1:6379. Connection refused.
```

## ✅ วิธีแก้ไข

### 1. **ตรวจสอบ Redis Service**
```bash
# ตรวจสอบสถานะ Redis
brew services list | grep redis

# เริ่ม Redis service
brew services start redis

# ทดสอบการเชื่อมต่อ
redis-cli ping
```

### 2. **ติดตั้ง Redis (ถ้ายังไม่มี)**
```bash
# ติดตั้ง Redis
brew install redis

# เริ่ม Redis service
brew services start redis

# ตั้งค่าให้เริ่มอัตโนมัติ
brew services enable redis
```

### 3. **ตรวจสอบการเชื่อมต่อ**
```bash
# ทดสอบ Redis โดยตรง
redis-cli ping

# ควรได้ผลลัพธ์: PONG
```

### 4. **ทดสอบ Django Cache**
```bash
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.development')
import django
django.setup()

from django.core.cache import cache
cache.set('test', 'Hello Redis!', 30)
print('Cache test:', cache.get('test'))
"
```

## 🚀 วิธีการเริ่ม Services

### วิธีที่ 1: ใช้สคริปต์
```bash
./start_services.sh
```

### วิธีที่ 2: เริ่มทีละตัว
```bash
# เริ่ม Redis
brew services start redis

# เริ่ม Django
python3 manage.py runserver 0.0.0.0:8000
```

### วิธีที่ 3: ใช้ Redis Manager
```bash
python3 redis_manager.py
```

## 🔍 การตรวจสอบปัญหา

### 1. **ตรวจสอบ Port**
```bash
# ตรวจสอบ port 6379
lsof -i :6379

# ตรวจสอบ port 8000
lsof -i :8000
```

### 2. **ตรวจสอบ Redis Logs**
```bash
# ดู Redis logs
tail -f /opt/homebrew/var/log/redis.log
```

### 3. **ทดสอบการเชื่อมต่อ**
```bash
# ทดสอบ Redis
redis-cli ping

# ทดสอบ Django
curl http://localhost:8000/admin/
```

## ⚙️ การตั้งค่า Redis

### 1. **ไฟล์ Config**
```bash
# ดู config file
cat /opt/homebrew/etc/redis.conf
```

### 2. **การตั้งค่าสำคัญ**
```conf
# Port
port 6379

# Bind address
bind 127.0.0.1

# Database
databases 16

# Log level
loglevel notice
```

## 🛠️ คำสั่งที่มีประโยชน์

### 1. **จัดการ Redis Service**
```bash
# เริ่ม Redis
brew services start redis

# หยุด Redis
brew services stop redis

# รีสตาร์ท Redis
brew services restart redis

# ดูสถานะ
brew services list | grep redis
```

### 2. **จัดการ Redis Data**
```bash
# เข้า Redis CLI
redis-cli

# ดู keys ทั้งหมด
redis-cli keys "*"

# ล้างข้อมูล
redis-cli flushall

# ออกจาก Redis CLI
exit
```

### 3. **ตรวจสอบ Performance**
```bash
# ดูข้อมูล Redis
redis-cli info

# ดู memory usage
redis-cli info memory

# ดู statistics
redis-cli info stats
```

## 🔧 การแก้ไขปัญหาเฉพาะ

### 1. **Port ถูกใช้งาน**
```bash
# หา process ที่ใช้ port 6379
lsof -i :6379

# ฆ่า process
kill -9 <PID>
```

### 2. **Permission Error**
```bash
# แก้ไข permission
sudo chown -R $(whoami) /opt/homebrew/var/
```

### 3. **Memory Error**
```bash
# ดู memory usage
redis-cli info memory

# ล้างข้อมูล
redis-cli flushall
```

## 📊 การ Monitor Redis

### 1. **ใช้ Redis CLI**
```bash
# Monitor commands
redis-cli monitor

# ดู real-time stats
redis-cli --stat
```

### 2. **ใช้ Python Script**
```bash
python3 redis_manager.py
```

## 🎯 การทดสอบ Admin Panel

### 1. **เข้าถึง Admin Panel**
```
URL: http://localhost:8000/admin/
Username: admin
Password: admin123
```

### 2. **ทดสอบการล็อกอิน**
```bash
python3 manage_users.py
```

## ⚠️ หมายเหตุ

- Redis ต้องทำงานก่อน Django
- ตรวจสอบ port 6379 ไม่ถูกใช้งานโดย process อื่น
- ใช้ `brew services` สำหรับจัดการ Redis service
- ตรวจสอบ logs เมื่อมีปัญหา

## 🆘 การขอความช่วยเหลือ

หากยังมีปัญหา ให้รันคำสั่งเหล่านี้และส่งผลลัพธ์มา:

```bash
# ตรวจสอบ services
brew services list

# ตรวจสอบ Redis
redis-cli ping

# ตรวจสอบ Django
python3 manage.py check

# ดู logs
tail -f /opt/homebrew/var/log/redis.log
```
