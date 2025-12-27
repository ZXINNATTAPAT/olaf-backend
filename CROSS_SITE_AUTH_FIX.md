# Cross-Site Authentication Fix

## ปัญหาที่พบ

เมื่อ Frontend อยู่ที่ `http://localhost:3000` และ Backend อยู่ที่ `https://web-production-ba20a.up.railway.app`, เกิดปัญหา **401 Unauthorized** เพราะ:

1. **Third-Party Cookie Blocking**: Browser ถือว่า cookies จาก Railway เป็น third-party cookies และไม่ส่งไปกับ request
2. **Cross-Site Request**: localhost และ railway.app เป็นคนละ site (ไม่ใช่แค่ cross-origin)
3. **Authentication Token ไม่ถูกส่ง**: ทำให้ API endpoints ที่ต้องการ authentication ส่ง 401

## การแก้ไข

### Backend Changes (✅ แก้ไขแล้ว)

#### 1. **Login & Register Endpoints** (`authentication/views.py`)

- ✅ เพิ่ม `access_token` และ `refresh_token` ใน response body
- ✅ ยังคง set cookies ไว้สำหรับ same-site requests

**Response Format:**

```json
{
  "message": "Login successful",
  "user": { ... },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 2. **Token Refresh Endpoint** (`/api/auth/refresh-token/`)

- ✅ ส่ง tokens กลับมาใน response body
- ✅ รองรับทั้ง cookies และ Authorization header

**Response Format:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 3. **Custom Authentication** (`authentication/authenticate.py`)

- ✅ ปรับให้ตรวจสอบ **Authorization header ก่อน** (สำหรับ cross-site)
- ✅ Fallback ไปใช้ cookies (สำหรับ same-site)
- ✅ เพิ่ม logging ที่ละเอียดขึ้น

**Authentication Priority:**

1. `Authorization: Bearer <token>` header (ใช้สำหรับ cross-site)
2. `access` cookie (ใช้สำหรับ same-site)

## Frontend Integration Guide

### วิธีใช้งานสำหรับ Frontend

#### 1. **Login/Register**

```typescript
// Login
const response = await axios.post(
  "/api/auth/login/",
  {
    email: "user@example.com",
    password: "password123",
  },
  {
    withCredentials: true, // ยังคงส่ง cookies ไว้
  }
);

// เก็บ tokens ใน localStorage
localStorage.setItem("access_token", response.data.access_token);
localStorage.setItem("refresh_token", response.data.refresh_token);
localStorage.setItem("user", JSON.stringify(response.data.user));
```

#### 2. **Authenticated Requests**

```typescript
// สร้าง axios instance ที่ส่ง Authorization header
const api = axios.create({
  baseURL: "https://web-production-ba20a.up.railway.app",
  withCredentials: true, // ยังคงส่ง cookies
});

// เพิ่ม interceptor เพื่อส่ง Authorization header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ใช้งาน
const posts = await api.post("/api/posts/create-with-image/", {
  header: "My Post",
  post_text: "Content...",
  image_url: "https://...",
});
```

#### 3. **Token Refresh**

```typescript
// Refresh token เมื่อ access token หมดอายุ
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // ถ้าได้ 401 และยังไม่ได้ retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");
        const response = await axios.post(
          "/api/auth/refresh-token/",
          { refresh: refreshToken }, // ส่งใน body
          {
            withCredentials: true,
            headers: {
              Authorization: `Bearer ${refreshToken}`, // หรือส่งใน header
            },
          }
        );

        // อัพเดท tokens
        localStorage.setItem("access_token", response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem("refresh_token", response.data.refresh_token);
        }

        // Retry request เดิมด้วย token ใหม่
        originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh ไม่สำเร็จ - ให้ logout
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

#### 4. **Logout**

```typescript
const logout = async () => {
  try {
    await api.post("/api/auth/logout/");
  } catch (error) {
    console.error("Logout error:", error);
  } finally {
    // ลบ tokens จาก localStorage
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    window.location.href = "/login";
  }
};
```

## Testing

### ทดสอบการทำงาน

1. **Login:**

```bash
curl -X POST https://web-production-ba20a.up.railway.app/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

2. **Create Post with Token:**

```bash
curl -X POST https://web-production-ba20a.up.railway.app/api/posts/create-with-image/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"header":"Test","post_text":"Content","image_url":"https://..."}'
```

3. **Refresh Token:**

```bash
curl -X POST https://web-production-ba20a.up.railway.app/api/auth/refresh-token/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN" \
  -d '{"refresh":"YOUR_REFRESH_TOKEN"}'
```

## สรุป

### ✅ สิ่งที่แก้ไขแล้ว:

1. Login/Register ส่ง tokens ใน response body
2. Token refresh ส่ง tokens ใน response body
3. Authentication รองรับ Authorization header (priority สูงกว่า cookies)
4. เพิ่ม logging สำหรับ debugging

### 📝 สิ่งที่ Frontend ต้องทำ:

1. เก็บ tokens ใน localStorage หลัง login/register
2. ส่ง `Authorization: Bearer <token>` header ในทุก authenticated request
3. Implement token refresh logic เมื่อได้ 401
4. ลบ tokens จาก localStorage เมื่อ logout

### 🔒 Security Notes:

- ยังคงใช้ HTTP-only cookies สำหรับ same-site requests (ปลอดภัยกว่า)
- localStorage ใช้เฉพาะกรณี cross-site (ไม่มีทางเลือกอื่น)
- CSRF token ยังคงใช้งานได้ตามปกติ
- Tokens มี expiration time (access: 1 hour, refresh: 7 days)

## Deployment

หลังจากแก้ไขโค้ดแล้ว ให้ deploy ไปที่ Railway:

```bash
git add .
git commit -m "Fix: Add token support in response body for cross-site authentication"
git push origin main
```

Railway จะ auto-deploy ให้อัตโนมัติ
