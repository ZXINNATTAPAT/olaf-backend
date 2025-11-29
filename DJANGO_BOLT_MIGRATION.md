# Django-Bolt Migration Guide

## ✅ สิ่งที่ทำเสร็จแล้ว

1. ✅ ติดตั้ง Django-Bolt สำเร็จ
2. ✅ อัปเดต PyJWT เป็น >=2.10.1
3. ✅ สร้าง Bolt API routes:
   - `blog/bolt_api.py` - Blog endpoints
   - `authentication/bolt_api.py` - Auth endpoints
4. ✅ สร้าง URL routing (`mysite/bolt_urls.py`)
5. ✅ อัปเดต settings.py (เพิ่ม django_bolt ใน INSTALLED_APPS)

## 📋 วิธีใช้งาน Django-Bolt

### Option 1: ใช้ Django-Bolt APIs (แนะนำ)

แก้ไข `mysite/urls.py`:

```python
from mysite import bolt_urls as bolt_urls_config

urlpatterns = [
    path('admin/', admin.site.urls),
    *bolt_urls_config.urlpatterns,  # Uncomment this line
    # ... rest
]
```

### Option 2: ใช้ Django REST Framework ต่อไป (Default)

ตอนนี้ยังใช้ DRF อยู่ตามปกติ สามารถ migrate ทีละส่วนได้

## 🚀 วิธีรัน

Django-Bolt ใช้ `APIView` เพื่อ integrate กับ Django URLs ดังนั้นใช้ Django's standard server:

```bash
# Development
python manage.py runserver

# Production
gunicorn mysite.wsgi --bind 0.0.0.0:8000
```

## 📝 API Endpoints

### Blog API (Bolt):
- `GET /api/posts` - List posts with pagination
- `GET /api/posts/{post_id}` - Get single post
- `POST /api/posts` - Create post

### Auth API (Bolt):
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register
- `POST /api/auth/logout` - Logout
- `GET /api/auth/user` - Get current user
- `GET /api/auth/check` - Check authentication
- `GET /api/auth/csrf` - Get CSRF token

## ⚠️ สิ่งที่ต้องทำต่อ

1. ⏳ เพิ่ม Authentication guards ใน Bolt APIs
2. ⏳ เพิ่ม Cookie handling สำหรับ JWT tokens
3. ⏳ Migrate endpoints อื่นๆ:
   - CloudDiary endpoints
   - Shared Images endpoints
   - Comments, Likes endpoints
4. ⏳ ทดสอบและปรับปรุง performance
5. ⏳ เพิ่ม error handling และ validation

## 🔧 Configuration

### Settings (mysite/settings.py)
- `django_bolt` อยู่ใน INSTALLED_APPS แล้ว
- CORS settings รองรับ Bolt APIs แล้ว
- ALLOWED_HOSTS รองรับ Bolt platform แล้ว

### URLs (mysite/urls.py)
- Bolt URLs ถูก comment ไว้ (uncomment เพื่อใช้งาน)
- DRF URLs ยังใช้งานได้ตามปกติ

## 📊 Performance

Django-Bolt ใช้ Rust-powered server (Actix Web):
- รองรับ 60k+ RPS
- Async/await support
- Type-safe serialization ด้วย msgspec

## 🐛 Troubleshooting

### Import errors
- ตรวจสอบว่า Django setup แล้ว (`django.setup()`)
- ตรวจสอบ Python version (ต้อง >= 3.10)

### API not working
- ตรวจสอบว่า uncomment Bolt URLs ใน `mysite/urls.py`
- ตรวจสอบว่า Bolt APIs import ได้

### Authentication issues
- ต้องเพิ่ม authentication guards ใน Bolt APIs
- ต้อง handle cookies สำหรับ JWT tokens

