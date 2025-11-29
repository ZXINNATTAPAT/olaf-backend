# Cookie Domain Fix - Final Solution

## ปัญหา
Cookies ไม่ถูกส่งไปกับ request จาก `localhost:3000` ไป `localhost:8000`

## สาเหตุ
Cookies ถูก set ที่ domain `localhost` แต่ browser ไม่ส่งไปกับ cross-origin request

## วิธีแก้ไข

### 1. ตั้งค่า Cookie Domain = None
```python
# authentication/services.py
cookie_domain = None  # ไม่ตั้ง domain
```

### 2. ใช้ SameSite=None และ Secure=False (สำหรับ localhost)
```python
# settings.py
'AUTH_COOKIE_SAMESITE': 'None',
'AUTH_COOKIE_SECURE': False,  # สำหรับ localhost
```

### 3. Frontend ใช้ withCredentials: true
```javascript
// httpClient.js
axiosInstance.interceptors.request.use((config) => {
  config.withCredentials = true;
  return config;
});
```

## ขั้นตอนการทดสอบ

1. **Restart Backend Server**
   ```bash
   cd olaf-backend
   source venv/bin/activate
   python manage.py runserver
   ```

2. **Clear All Cookies**
   - DevTools → Application → Cookies
   - ลบ cookies ทั้งหมด (ทั้ง `localhost` และ `localhost:8000`)

3. **Login ใหม่**
   - Login ผ่าน frontend
   - ตรวจสอบ backend logs ว่า cookies ถูก set ที่ domain อะไร

4. **ตรวจสอบ Cookies**
   - DevTools → Application → Cookies → `http://localhost:8000`
   - ควรเห็น cookies: `access`, `refresh`, `csrftoken`
   - Domain ควรเป็น `localhost:8000` (ไม่ใช่ `localhost`)

5. **ทดสอบ Request**
   - สร้างโพสต์หรือ request อื่นๆ
   - ตรวจสอบ Network tab → Request Headers → Cookie
   - ควรเห็น: `Cookie: access=...; refresh=...; csrftoken=...`

## หมายเหตุ

- Cookies ที่ set ที่ `domain=None` จะถูก set ที่ exact domain (`localhost:8000`)
- ด้วย `SameSite=None` และ `withCredentials:true`, cookies จะถูกส่งจาก `localhost:3000` ไป `localhost:8000`
- ถ้ายังไม่ได้ผล ให้ตรวจสอบ browser settings หรือลองใช้ Incognito mode

