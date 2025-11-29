# Cookie Authentication Fix - 2025

## ปัญหาที่พบ

เมื่อพยายามสร้างโพสต์ เกิด error 401 Unauthorized:
- Request ไปที่ `/api/posts/create-with-image/` ได้รับ 401
- Token refresh ก็ล้มเหลวเพราะไม่มี refresh token cookie
- Error message: "No valid refresh token found"

## สาเหตุที่เป็นไปได้

1. **Cookies หมดอายุ** - Access token หมดอายุใน 1 ชั่วโมง, Refresh token หมดอายุใน 7 วัน
2. **Cookies ไม่ถูกส่ง** - Browser ไม่ส่ง cookies ไปกับ request
3. **Cookies ไม่ถูก set** - Login ไม่ได้ set cookies อย่างถูกต้อง

## การแก้ไขที่ทำ

### 1. เพิ่ม Logging ใน Backend
- เพิ่ม logging ใน `create_post_with_image` เพื่อดู cookies ที่ได้รับ
- เพิ่ม logging ใน `CustomAuthentication` เพื่อดู authentication status

### 2. เพิ่ม CORS Headers
- ตรวจสอบว่า CORS headers ถูก set ใน response
- ใช้ origin จาก request header

### 3. ตรวจสอบ Cookie Settings
- `AUTH_COOKIE_SAMESITE = 'None'` (สำหรับ cross-origin)
- `AUTH_COOKIE_SECURE = False` (สำหรับ development)
- `AUTH_COOKIE_DOMAIN = None` (ใช้ request domain)

## วิธีแก้ไขปัญหา

### ขั้นตอนที่ 1: ตรวจสอบ Cookies
1. เปิด DevTools → Application → Cookies
2. ตรวจสอบว่ามี cookies ต่อไปนี้หรือไม่:
   - `access` (access token)
   - `refresh` (refresh token)
   - `csrftoken` (CSRF token)

### ขั้นตอนที่ 2: Login ใหม่
หากไม่มี cookies หรือหมดอายุ:
1. Logout จากระบบ
2. Login ใหม่
3. ตรวจสอบว่า cookies ถูก set ใน Application tab

### ขั้นตอนที่ 3: ตรวจสอบ Network Tab
1. เปิด DevTools → Network
2. ดู request ไปที่ `/api/posts/create-with-image/`
3. ตรวจสอบ Request Headers → Cookie:
   - ควรมี `access=...` และ `refresh=...`
4. ตรวจสอบ Response Headers:
   - ควรมี `Set-Cookie` headers (ถ้า login ใหม่)

### ขั้นตอนที่ 4: ตรวจสอบ Backend Logs
ดู backend logs เพื่อดู:
```
🔍 Authentication attempt - Cookies received: [...]
📝 Create post request - Cookies received: [...]
```

## การตั้งค่า Cookies

### Development (localhost)
```python
AUTH_COOKIE_SECURE = False
AUTH_COOKIE_SAMESITE = 'None'
AUTH_COOKIE_DOMAIN = None
```

### Production
```python
AUTH_COOKIE_SECURE = True  # ต้องใช้ HTTPS
AUTH_COOKIE_SAMESITE = 'None'
AUTH_COOKIE_DOMAIN = None  # หรือ set domain ถ้าต้องการ
```

## หมายเหตุ

1. **HttpOnly Cookies**: `access` และ `refresh` เป็น HttpOnly - JavaScript ไม่สามารถอ่านได้ (เพื่อความปลอดภัย)
2. **SameSite=None**: ต้องใช้ `Secure=True` ใน production, แต่ Chrome อนุญาต `Secure=False` สำหรับ localhost
3. **Cross-Origin**: Frontend (localhost:3000) และ Backend (localhost:8000) เป็น cross-origin ดังนั้นต้องใช้ `SameSite=None`

## Testing

หลังจากแก้ไข:
1. Login ใหม่
2. ตรวจสอบ cookies ใน Application tab
3. ลองสร้างโพสต์ใหม่
4. ตรวจสอบ backend logs เพื่อดู cookies ที่ได้รับ

