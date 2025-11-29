# Django-Bolt Setup Guide

## สถานะการติดตั้ง

✅ Django-Bolt ติดตั้งสำเร็จแล้ว
✅ PyJWT อัปเดตเป็น >=2.10.1 แล้ว
✅ Bolt API routes สร้างเสร็จแล้ว

## โครงสร้างไฟล์

### Bolt API Files:
- `blog/bolt_api.py` - Blog endpoints (posts, comments)
- `authentication/bolt_api.py` - Authentication endpoints
- `mysite/bolt_urls.py` - URL routing สำหรับ Bolt APIs
- `run_bolt.py` - Script สำหรับรัน Django-Bolt server

## วิธีใช้งาน

### 1. รัน Django-Bolt Server (Standalone)

```bash
cd /Users/zxin/Documents/ZXIN/1_PERSONAL/MYPJ/SOFTTEST/olaf-backend
source venv/bin/activate
python run_bolt.py
```

### 2. ใช้ร่วมกับ Django URLs (Hybrid)

แก้ไข `mysite/urls.py` เพื่อ uncomment Bolt URLs:

```python
from mysite import bolt_urls as bolt_urls_config

urlpatterns = [
    path('admin/', admin.site.urls),
    *bolt_urls_config.urlpatterns,  # Uncomment this line
    # ... rest of URLs
]
```

### 3. ใช้ Django REST Framework ต่อไป (Default)

ตอนนี้ยังใช้ DRF อยู่ตามปกติ สามารถ migrate ไป Bolt ทีละส่วนได้

## API Endpoints

### Blog API (Bolt):
- `GET /api/posts` - List posts
- `GET /api/posts/{post_id}` - Get post
- `POST /api/posts` - Create post

### Auth API (Bolt):
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register
- `POST /api/auth/logout` - Logout
- `GET /api/auth/user` - Get user
- `GET /api/auth/check` - Check auth
- `GET /api/auth/csrf` - Get CSRF token

## สิ่งที่ต้องทำต่อ

1. ✅ ติดตั้ง Django-Bolt
2. ✅ สร้าง Bolt API routes
3. ⏳ เพิ่ม Authentication guards
4. ⏳ เพิ่ม Cookie handling
5. ⏳ Migrate endpoints อื่นๆ (CloudDiary, Shared Images)
6. ⏳ ทดสอบและปรับปรุง

## หมายเหตุ

- Django-Bolt ใช้ Rust-powered server (Actix Web) ซึ่งเร็วกว่า gunicorn มาก
- Performance: รองรับ 60k+ RPS
- ยังคงใช้ Django ORM ได้ตามปกติ
- รองรับ async/await

## Troubleshooting

### Error: "mount_bolt_api not found"
- Django-Bolt ใช้ `APIView` แทน `mount_bolt_api`
- ดู `mysite/bolt_urls.py` สำหรับตัวอย่าง

### Error: "run_server signature mismatch"
- ตรวจสอบ Django-Bolt version และ docs
- `run_bolt.py` มี fallback สำหรับ signature ที่แตกต่าง

### Error: "Import errors"
- ตรวจสอบว่า Django setup แล้วก่อน import models
- ใช้ `django.setup()` ใน `run_bolt.py`

