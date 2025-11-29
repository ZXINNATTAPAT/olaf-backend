# Cookie Debugging Guide

## ปัญหาที่พบ

Frontend ไม่เห็น `Set-Cookie` headers และ CORS headers ใน response

## สาเหตุ

### 1. Set-Cookie เป็น Forbidden Header
**สำคัญ**: `Set-Cookie` เป็น forbidden header ที่ JavaScript **ไม่สามารถอ่านได้** โดยตรงผ่าน `response.headers.get('Set-Cookie')`

Browser จะ set cookies อัตโนมัติเมื่อได้รับ `Set-Cookie` header แต่ JavaScript ไม่สามารถอ่าน header นี้ได้

### 2. CORS Headers
CORS headers ถูกเพิ่มโดย `django-cors-headers` middleware อัตโนมัติ แต่ frontend อาจไม่เห็นเพราะ:
- Browser filter headers บางตัว
- Headers ไม่ถูก expose อย่างถูกต้อง

## วิธีตรวจสอบว่า Cookies ถูก Set หรือไม่

### วิธีที่ 1: ตรวจสอบใน Browser DevTools

1. **Network Tab**:
   - เปิด DevTools → Network
   - Login แล้วดู response ของ `/api/auth/login/`
   - ดู **Response Headers** (ไม่ใช่ Request Headers)
   - ควรเห็น:
     ```
     Set-Cookie: access=...; Path=/; SameSite=None
     Set-Cookie: refresh=...; Path=/; SameSite=None
     Set-Cookie: csrftoken=...; Path=/
     Access-Control-Allow-Origin: http://localhost:3000
     Access-Control-Allow-Credentials: true
     ```

2. **Application/Storage Tab**:
   - เปิด DevTools → Application (Chrome) หรือ Storage (Firefox)
   - ไปที่ **Cookies** → `http://127.0.0.1:8000` หรือ `http://localhost:8000`
   - ตรวจสอบว่ามี cookies:
     - `access`
     - `refresh`
     - `csrftoken`

### วิธีที่ 2: ตรวจสอบใน Frontend Code

```javascript
// ❌ วิธีนี้จะไม่ทำงาน - Set-Cookie เป็น forbidden header
const setCookieHeader = response.headers.get('Set-Cookie');
console.log('Set-Cookie:', setCookieHeader); // จะได้ null

// ✅ วิธีที่ถูกต้อง - ตรวจสอบ cookies หลังจาก response
// หลังจาก login สำเร็จ
function checkCookies() {
    const cookies = document.cookie.split(';').reduce((acc, cookie) => {
        const [key, value] = cookie.trim().split('=');
        acc[key] = value;
        return acc;
    }, {});
    
    console.log('Cookies:', cookies);
    console.log('Has access token:', !!cookies.access);
    console.log('Has refresh token:', !!cookies.refresh);
    console.log('Has CSRF token:', !!cookies.csrftoken);
}

// เรียกใช้หลังจาก login
checkCookies();
```

### วิธีที่ 3: ตรวจสอบ Backend Logs

หลัง login สำเร็จ ควรเห็น logs แบบนี้:

```
INFO: Setting cookies - Domain: None, SameSite: None, Secure: False
INFO: Access token length: 200
INFO: Refresh token length: 250
INFO: ✅ Set access token cookie: access
INFO: ✅ Set refresh token cookie: refresh
INFO: Login response headers: {...}
INFO: User user@example.com logged in successfully
```

## การแก้ไขที่ทำไปแล้ว

### 1. Cookie Settings
- ✅ ตั้งค่า `AUTH_COOKIE_SAMESITE = 'None'` สำหรับ cross-origin
- ✅ ตั้งค่า `AUTH_COOKIE_SECURE = False` สำหรับ development (localhost)
- ✅ ตั้งค่า `AUTH_COOKIE_HTTP_ONLY = True` เพื่อความปลอดภัย

### 2. CORS Settings
- ✅ `CORS_ALLOW_CREDENTIALS = True`
- ✅ `CORS_ALLOWED_ORIGINS` รวม `http://localhost:3000` และ `http://127.0.0.1:3000`
- ✅ เพิ่ม explicit CORS headers ใน login response

### 3. Logging
- ✅ เพิ่ม detailed logging ใน `set_auth_cookies()`
- ✅ Log cookie settings และ response headers

## Frontend Code ที่ถูกต้อง

### 1. Login Request

```javascript
async function login(email, password) {
    const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',  // ⚠️ สำคัญมาก!
        body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) {
        throw new Error('Login failed');
    }
    
    const data = await response.json();
    
    // ✅ ตรวจสอบ CORS headers (ถ้าต้องการ)
    const allowOrigin = response.headers.get('Access-Control-Allow-Origin');
    const allowCredentials = response.headers.get('Access-Control-Allow-Credentials');
    console.log('CORS Headers:', { allowOrigin, allowCredentials });
    
    // ❌ ไม่สามารถอ่าน Set-Cookie header ได้
    // const setCookie = response.headers.get('Set-Cookie'); // จะได้ null
    
    // ✅ ตรวจสอบ cookies หลังจาก response
    // Cookies จะถูก set อัตโนมัติโดย browser
    // ตรวจสอบผ่าน document.cookie หรือ Application tab
    
    return data;
}
```

### 2. ตรวจสอบ Cookies

```javascript
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function checkAuthCookies() {
    const access = getCookie('access');
    const refresh = getCookie('refresh');
    const csrf = getCookie('csrftoken');
    
    return {
        hasAccessToken: !!access,
        hasRefreshToken: !!refresh,
        hasCSRFToken: !!csrf,
        accessToken: access,
        refreshToken: refresh,
        csrfToken: csrf
    };
}

// เรียกใช้หลังจาก login
const cookieStatus = checkAuthCookies();
console.log('🍪 Cookie Status:', cookieStatus);
```

### 3. Authenticated Requests

```javascript
async function authenticatedRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        credentials: 'include',  // ⚠️ สำคัญ - ต้องส่ง cookies
    });
    
    return response;
}
```

## Troubleshooting

### ปัญหา: Cookies ไม่ถูก Set

**ตรวจสอบ**:
1. ✅ Backend logs - ดูว่ามี "✅ Set access token cookie" หรือไม่
2. ✅ Network tab - ดู Response Headers ว่ามี `Set-Cookie` หรือไม่
3. ✅ Application tab - ดูว่ามี cookies ใน browser หรือไม่
4. ✅ Frontend ใช้ `credentials: 'include'` หรือไม่

**แก้ไข**:
- ตรวจสอบ CORS settings
- ตรวจสอบ cookie settings (SameSite, Secure, Domain)
- ตรวจสอบว่า frontend และ backend ใช้ domain ที่ถูกต้อง

### ปัญหา: CORS Headers ไม่เห็น

**ตรวจสอบ**:
1. ✅ `CORS_ALLOWED_ORIGINS` รวม frontend origin หรือไม่
2. ✅ `CORS_ALLOW_CREDENTIALS = True` หรือไม่
3. ✅ `CorsMiddleware` อยู่ใน `MIDDLEWARE` หรือไม่

**แก้ไข**:
- เพิ่ม frontend origin ใน `CORS_ALLOWED_ORIGINS`
- ตรวจสอบ middleware order

### ปัญหา: Cookies ไม่ถูกส่งใน Request ถัดไป

**ตรวจสอบ**:
1. ✅ Frontend ใช้ `credentials: 'include'` ในทุก request หรือไม่
2. ✅ Cookie domain และ path ถูกต้องหรือไม่
3. ✅ Cookies ยังไม่หมดอายุหรือไม่

**แก้ไข**:
- ใช้ `credentials: 'include'` ในทุก fetch request
- ตรวจสอบ cookie settings

## Testing Checklist

- [ ] Backend logs แสดง "✅ Set access token cookie"
- [ ] Network tab แสดง `Set-Cookie` headers ใน Response Headers
- [ ] Application tab แสดง cookies (`access`, `refresh`, `csrftoken`)
- [ ] Frontend สามารถอ่าน cookies ผ่าน `document.cookie`
- [ ] Authenticated requests ทำงานได้ (cookies ถูกส่งอัตโนมัติ)
- [ ] CORS headers ถูกต้อง (`Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials`)

## Notes

1. **Set-Cookie Header**: JavaScript ไม่สามารถอ่านได้ - ใช้ Application tab หรือ `document.cookie` แทน
2. **HttpOnly Cookies**: `access` และ `refresh` เป็น HttpOnly - JavaScript ไม่สามารถอ่านได้โดยตรง (เพื่อความปลอดภัย)
3. **CSRF Token**: สามารถอ่านได้ผ่าน `document.cookie` หรือ header `X-CSRFToken`
4. **SameSite=None**: ต้องใช้ `Secure=True` ใน production (HTTPS) แต่ Chrome อนุญาต `Secure=False` สำหรับ localhost

## Production Settings

เมื่อ deploy ไป production:

```python
DEBUG = False
AUTH_COOKIE_SECURE = True  # ต้องใช้ HTTPS
AUTH_COOKIE_SAMESITE = 'None'  # สำหรับ cross-origin
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com"
]
```

