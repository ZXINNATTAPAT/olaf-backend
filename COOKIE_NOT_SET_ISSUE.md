# Cookie Not Set Issue - Debugging Guide

## ปัญหาที่พบ

จาก logs:
```
🍪 Cookie Status: {hasAccessToken: false, hasRefreshToken: false}
❌ Refresh token failed: "No valid refresh token found"
POST /api/posts/create-with-image/ 401 (Unauthorized)
```

**สรุป**: Cookies ไม่ถูก set หลัง login ทำให้:
1. ไม่สามารถ authenticate ได้ (401 Unauthorized)
2. ไม่สามารถ refresh token ได้ (401 Unauthorized)

## สาเหตุที่เป็นไปได้

### 1. Backend ไม่ส่ง Set-Cookie Headers
**ตรวจสอบ**: ดู backend logs หลัง login
```
INFO: ✅ Set access token cookie: access
INFO: ✅ Set refresh token cookie: refresh
```

**หากไม่เห็น logs เหล่านี้**: Server อาจไม่ได้ restart หรือ code ไม่ถูก update

### 2. Browser Block Cookies
**ตรวจสอบ**: 
- Network tab → Response Headers → ดูว่ามี `Set-Cookie` headers หรือไม่
- Application tab → Cookies → ดูว่ามี cookies หรือไม่

### 3. CORS Settings ไม่ถูกต้อง
**ตรวจสอบ**:
- `CORS_ALLOW_CREDENTIALS = True`
- `CORS_ALLOWED_ORIGINS` รวม frontend origin
- Response headers มี `Access-Control-Allow-Credentials: true`

### 4. SameSite=None กับ Secure=False
**ปัญหา**: Chrome อาจ block cookies ถ้า `SameSite=None` แต่ `Secure=False` (ยกเว้น localhost)

**แก้ไข**: 
- สำหรับ localhost: ใช้ `SameSite=None` และ `Secure=False` (Chrome อนุญาต)
- ตรวจสอบว่าใช้ `http://localhost:3000` ไม่ใช่ `http://127.0.0.1:3000`

### 5. Domain Mismatch
**ปัญหา**: Frontend อยู่ที่ `localhost:3000` แต่ backend อยู่ที่ `127.0.0.1:8000`

**แก้ไข**: ใช้ domain เดียวกัน:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000` (แทน `127.0.0.1:8000`)

## วิธีตรวจสอบ

### Step 1: ตรวจสอบ Backend Logs

หลัง login ควรเห็น:
```
INFO: Setting cookies - Domain: None, SameSite: None, Secure: False
INFO: Access token length: 200
INFO: Refresh token length: 250
INFO: ✅ Set access token cookie: access
INFO: ✅ Set refresh token cookie: refresh
INFO: Origin: http://localhost:3000, CORS headers set: True
```

**หากไม่เห็น logs เหล่านี้**:
1. Restart Django server
2. ตรวจสอบว่า code ถูก update แล้ว
3. ตรวจสอบว่า login endpoint ถูกเรียก

### Step 2: ตรวจสอบ Network Tab

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

**หากไม่เห็น Set-Cookie headers**:
- Backend ไม่ส่ง cookies
- ตรวจสอบ backend logs
- ตรวจสอบว่า `response.set_cookie()` ถูกเรียก

### Step 3: ตรวจสอบ Application Tab

1. เปิด DevTools → Application (Chrome) หรือ Storage (Firefox)
2. ไปที่ **Cookies** → `http://127.0.0.1:8000` หรือ `http://localhost:8000`
3. ควรเห็น cookies:
   - `access`
   - `refresh`
   - `csrftoken`

**หากไม่เห็น cookies**:
- Cookies ถูก block โดย browser
- ตรวจสอบ browser settings
- ตรวจสอบ CORS settings

### Step 4: ตรวจสอบ Frontend Code

```javascript
// ต้องใช้ credentials: 'include' ในทุก request
fetch('http://127.0.0.1:8000/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    credentials: 'include',  // ⚠️ สำคัญมาก!
    body: JSON.stringify({ email, password })
})
```

**ตรวจสอบ**:
- Frontend ใช้ `credentials: 'include'` หรือไม่
- Frontend ใช้ `withCredentials: true` ใน axios หรือไม่

### Step 5: ทดสอบ Test Endpoint

```bash
curl -X GET "http://127.0.0.1:8000/api/auth/test-cookies/" \
  -H "Origin: http://localhost:3000" \
  -v
```

หรือจาก frontend:
```javascript
fetch('http://127.0.0.1:8000/api/auth/test-cookies/', {
    credentials: 'include'
})
.then(r => r.json())
.then(data => {
    console.log('Test cookies:', data);
    // ตรวจสอบ cookies ใน Application tab
});
```

## วิธีแก้ไข

### Fix 1: Restart Django Server
```bash
# หยุด server (Ctrl+C)
source venv/bin/activate && python3 manage.py runserver
```

### Fix 2: ตรวจสอบ Settings
```python
# mysite/settings.py
DEBUG = True  # สำหรับ development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
AUTH_COOKIE_SAMESITE = 'None'  # สำหรับ cross-origin
AUTH_COOKIE_SECURE = False  # สำหรับ development (localhost)
```

### Fix 3: ใช้ Same Domain
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000` (แทน `127.0.0.1:8000`)

### Fix 4: ตรวจสอบ Browser Settings
- เปิด DevTools → Application → Cookies
- ตรวจสอบว่า cookies ถูก block หรือไม่
- ลองใช้ browser อื่น (Chrome, Firefox, Safari)

### Fix 5: ตรวจสอบ CORS Headers
Response headers ต้องมี:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
```

## Debugging Checklist

- [ ] Backend logs แสดง "✅ Set access token cookie"
- [ ] Network tab แสดง `Set-Cookie` headers ใน Response Headers
- [ ] Application tab แสดง cookies (`access`, `refresh`, `csrftoken`)
- [ ] Frontend ใช้ `credentials: 'include'`
- [ ] CORS settings ถูกต้อง
- [ ] Origin อยู่ใน `CORS_ALLOWED_ORIGINS`
- [ ] Server restarted แล้ว
- [ ] ใช้ same domain (localhost:3000 → localhost:8000)

## Next Steps

1. **ตรวจสอบ Backend Logs**: ดูว่ามี "✅ Set access token cookie" หรือไม่
2. **ตรวจสอบ Network Tab**: ดู Response Headers ว่ามี `Set-Cookie` หรือไม่
3. **ตรวจสอบ Application Tab**: ดูว่ามี cookies หรือไม่
4. **ทดสอบ Test Endpoint**: ใช้ `/api/auth/test-cookies/` เพื่อทดสอบ

## หากยังไม่ทำงาน

1. ตรวจสอบ backend logs
2. ตรวจสอบ Network tab → Response Headers
3. ตรวจสอบ Application tab → Cookies
4. ทดสอบ test endpoint
5. ตรวจสอบ browser console สำหรับ errors

## Contact

หากยังมีปัญหา ให้ส่ง:
1. Backend logs (หลัง login)
2. Network tab screenshot (Response Headers)
3. Application tab screenshot (Cookies)
4. Browser console errors

