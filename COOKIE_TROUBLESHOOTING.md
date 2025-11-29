# Cookie Troubleshooting Guide

## ปัญหาที่พบ

Cookies ไม่ถูก set หลัง login แม้ว่า backend จะเรียก `response.set_cookie()` แล้ว

## การตรวจสอบ

### 1. ตรวจสอบ Backend Logs

หลัง login สำเร็จ ควรเห็น logs แบบนี้:

```
INFO: Setting cookies - Domain: None, SameSite: None, Secure: False
INFO: Access token length: 200
INFO: Refresh token length: 250
INFO: ✅ Set access token cookie: access
INFO: ✅ Set refresh token cookie: refresh
INFO: Login response headers: {...}
```

**หากไม่เห็น logs เหล่านี้**: Server อาจไม่ได้ restart หรือ code ไม่ถูก update

### 2. ใช้ Test Endpoint

เรียกใช้ test endpoint เพื่อตรวจสอบว่า cookies ทำงานหรือไม่:

```bash
# จาก frontend หรือ curl
curl -X GET "http://127.0.0.1:8000/api/auth/test-cookies/" \
  -H "Origin: http://localhost:3000" \
  -v
```

หรือจาก frontend:

```javascript
fetch('http://127.0.0.1:8000/api/auth/test-cookies/', {
    method: 'GET',
    credentials: 'include',
    headers: {
        'Origin': 'http://localhost:3000'
    }
})
.then(res => res.json())
.then(data => {
    console.log('Test cookies response:', data);
    // ตรวจสอบ cookies ใน Application tab
});
```

### 3. ตรวจสอบ Network Tab

1. เปิด DevTools → Network
2. Login แล้วดู response ของ `/api/auth/login/`
3. ดู **Response Headers** (ไม่ใช่ Request Headers)
4. ควรเห็น:
   ```
   Set-Cookie: access=...; Path=/; SameSite=None
   Set-Cookie: refresh=...; Path=/; SameSite=None
   Access-Control-Allow-Origin: http://localhost:3000
   Access-Control-Allow-Credentials: true
   ```

### 4. ตรวจสอบ Application Tab

1. เปิด DevTools → Application (Chrome) หรือ Storage (Firefox)
2. ไปที่ **Cookies** → `http://127.0.0.1:8000`
3. ควรเห็น cookies:
   - `access`
   - `refresh`
   - `csrftoken`

## สาเหตุที่เป็นไปได้

### 1. Server ไม่ได้ Restart

**แก้ไข**: Restart Django server

```bash
# หยุด server (Ctrl+C)
# แล้วรันใหม่
source venv/bin/activate && python3 manage.py runserver
```

### 2. Frontend ไม่ส่ง `credentials: 'include'`

**แก้ไข**: ตรวจสอบว่า frontend ส่ง `credentials: 'include'` ในทุก request

```javascript
fetch('http://127.0.0.1:8000/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    credentials: 'include',  // ⚠️ สำคัญมาก!
    body: JSON.stringify({ email, password })
})
```

### 3. Origin ไม่ตรงกับ CORS_ALLOWED_ORIGINS

**ตรวจสอบ**:
- Frontend ใช้ origin อะไร? (`http://localhost:3000` หรือ `http://127.0.0.1:3000`?)
- Origin อยู่ใน `CORS_ALLOWED_ORIGINS` หรือไม่?

**แก้ไข**: เพิ่ม origin ใน `CORS_ALLOWED_ORIGINS` ใน `settings.py`

### 4. SameSite=None แต่ Secure=False

**ปัญหา**: Chrome อาจ block cookies ถ้า `SameSite=None` แต่ `Secure=False` (ยกเว้น localhost)

**แก้ไข**: 
- สำหรับ localhost: ใช้ `SameSite=None` และ `Secure=False` (Chrome อนุญาต)
- สำหรับ production: ใช้ `SameSite=None` และ `Secure=True` (ต้องใช้ HTTPS)

### 5. Domain Mismatch

**ปัญหา**: Frontend อยู่ที่ `localhost:3000` แต่ backend อยู่ที่ `127.0.0.1:8000`

**แก้ไข**: ใช้ domain เดียวกัน:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000` (แทน `127.0.0.1:8000`)

### 6. Response Headers ถูก Override

**ปัญหา**: django-cors-headers middleware อาจ override headers

**แก้ไข**: ตรวจสอบ middleware order ใน `settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "corsheaders.middleware.CorsMiddleware",  # ต้องอยู่ก่อน CommonMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

## Debugging Steps

### Step 1: ตรวจสอบ Settings

```bash
python3 manage.py shell
```

```python
from django.conf import settings
print('DEBUG:', settings.DEBUG)
print('CORS_ALLOWED_ORIGINS:', settings.CORS_ALLOWED_ORIGINS)
print('CORS_ALLOW_CREDENTIALS:', settings.CORS_ALLOW_CREDENTIALS)
print('AUTH_COOKIE_SAMESITE:', settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
print('AUTH_COOKIE_SECURE:', settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'])
```

### Step 2: ทดสอบ Test Endpoint

```bash
curl -X GET "http://127.0.0.1:8000/api/auth/test-cookies/" \
  -H "Origin: http://localhost:3000" \
  -v
```

ดู response headers ว่ามี `Set-Cookie` หรือไม่

### Step 3: ตรวจสอบ Login Response

1. Login จาก frontend
2. ดู Network tab → Response Headers
3. ดู backend logs
4. ดู Application tab → Cookies

### Step 4: ตรวจสอบ Frontend Code

```javascript
// ตรวจสอบว่า credentials: 'include' ถูกส่งหรือไม่
fetch('http://127.0.0.1:8000/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    credentials: 'include',  // ⚠️ ต้องมี!
    body: JSON.stringify({ email, password })
})
.then(async (res) => {
    // ตรวจสอบ response headers
    console.log('Response headers:', {
        'Access-Control-Allow-Origin': res.headers.get('Access-Control-Allow-Origin'),
        'Access-Control-Allow-Credentials': res.headers.get('Access-Control-Allow-Credentials'),
        'X-CSRFToken': res.headers.get('X-CSRFToken'),
    });
    
    // ตรวจสอบ cookies (หลังจาก response)
    const cookies = document.cookie.split(';').reduce((acc, cookie) => {
        const [key, value] = cookie.trim().split('=');
        acc[key] = value;
        return acc;
    }, {});
    console.log('Cookies after login:', cookies);
    
    return res.json();
});
```

## Quick Fix Checklist

- [ ] Restart Django server
- [ ] ตรวจสอบว่า frontend ส่ง `credentials: 'include'`
- [ ] ตรวจสอบว่า origin อยู่ใน `CORS_ALLOWED_ORIGINS`
- [ ] ตรวจสอบ Network tab → Response Headers
- [ ] ตรวจสอบ Application tab → Cookies
- [ ] ตรวจสอบ backend logs
- [ ] ทดสอบ test endpoint (`/api/auth/test-cookies/`)

## Test Endpoint

ใช้ endpoint นี้เพื่อทดสอบว่า cookies ทำงานหรือไม่:

```
GET /api/auth/test-cookies/
```

Response จะแสดง:
- Cookie settings
- CORS settings
- Cookies ที่ได้รับ
- Origin ที่ส่งมา

## Contact

หากยังมีปัญหา ให้ตรวจสอบ:
1. Backend logs
2. Network tab → Response Headers
3. Application tab → Cookies
4. Test endpoint response

