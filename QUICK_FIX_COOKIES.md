# Quick Fix: Cookies Not Being Set

## ปัญหา
Cookies ไม่ถูก set หลัง login

## วิธีแก้ไขด่วน

### 1. Restart Django Server
```bash
# หยุด server (Ctrl+C)
source venv/bin/activate && python3 manage.py runserver
```

### 2. ตรวจสอบ Backend Logs
หลัง login ควรเห็น:
```
INFO: ✅ Set access token cookie: access
INFO: ✅ Set refresh token cookie: refresh
```

### 3. ตรวจสอบ Network Tab
1. DevTools → Network
2. ดู `/api/auth/login/` response
3. ดู **Response Headers** ว่ามี `Set-Cookie` หรือไม่

### 4. ตรวจสอบ Frontend
ต้องใช้ `credentials: 'include'`:
```javascript
fetch('http://127.0.0.1:8000/api/auth/login/', {
    method: 'POST',
    credentials: 'include',  // ⚠️ สำคัญ!
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
})
```

### 5. ทดสอบ Test Endpoint
```javascript
fetch('http://127.0.0.1:8000/api/auth/test-cookies/', {
    credentials: 'include'
})
.then(r => r.json())
.then(console.log)
```

## Checklist
- [ ] Server restarted
- [ ] Backend logs แสดง "✅ Set access token cookie"
- [ ] Network tab แสดง `Set-Cookie` headers
- [ ] Frontend ใช้ `credentials: 'include'`
- [ ] Application tab แสดง cookies

## หากยังไม่ทำงาน
ดูรายละเอียดใน `COOKIE_TROUBLESHOOTING.md`

