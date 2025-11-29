# วิธีตรวจสอบ Cookies

## ปัญหาที่พบ
Request มีแค่ `csrftoken` cookie แต่ไม่มี `access` และ `refresh` cookies

## วิธีตรวจสอบ

### 1. ตรวจสอบ Login Response
1. เปิด DevTools → Network tab
2. Login ใหม่
3. ดู request ไปที่ `/api/auth/login/`
4. ดู Response Headers → ควรมี `Set-Cookie` headers:
   - `Set-Cookie: access=...`
   - `Set-Cookie: refresh=...`
   - `Set-Cookie: csrftoken=...`

### 2. ตรวจสอบ Application Tab
1. เปิด DevTools → Application tab
2. ไปที่ Cookies → `http://localhost:3000`
3. ตรวจสอบว่ามี cookies:
   - `access` (HttpOnly)
   - `refresh` (HttpOnly)
   - `csrftoken`

### 3. ตรวจสอบ Backend Logs
ดู backend logs หลัง login ควรเห็น:
```
🍪 START: set_auth_cookies() called
✅ Set access token cookie: access
✅ Set refresh token cookie: refresh
🍪 END: set_auth_cookies() completed
```

### 4. ตรวจสอบ Cookie Settings
ใน settings.py:
- `AUTH_COOKIE_SAMESITE = 'None'` (สำหรับ cross-origin)
- `AUTH_COOKIE_SECURE = False` (สำหรับ localhost)
- `AUTH_COOKIE_DOMAIN = None` (ใช้ request domain)

## สาเหตุที่เป็นไปได้

1. **Cookies ไม่ถูก set** - ตรวจสอบ backend logs
2. **Cookies หมดอายุ** - Login ใหม่
3. **Browser block cookies** - ตรวจสอบ SameSite/Secure settings
4. **Domain mismatch** - ตรวจสอบว่าใช้ localhost ทั้งหมด

## วิธีแก้ไข

1. **Login ใหม่** - Logout แล้ว login ใหม่
2. **Clear cookies** - Clear browser cookies แล้ว login ใหม่
3. **ตรวจสอบ backend logs** - ดูว่า cookies ถูก set หรือไม่
4. **ตรวจสอบ Network tab** - ดู Set-Cookie headers ใน login response

