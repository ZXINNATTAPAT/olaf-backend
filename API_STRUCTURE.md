# API Request Structure สำหรับ Frontend

## Base URL
```
https://olaf-backend.onrender.com/api/auth/
```

## 1. ขอ CSRF Token
```http
GET /api/auth/csrf/
```

**Headers:**
```
None (ไม่ต้องส่ง headers)
```

**Response:**
```json
{
    "message": "CSRF token set in cookie"
}
```

**Response Headers:**
```
X-CSRFToken: <csrf_token_value>
Set-Cookie: csrftoken=<csrf_token_value>; Path=/
```

---

## 2. User Registration
```http
POST /api/auth/register/
```

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "0812345678",
    "password": "secure_password123",
    "password2": "secure_password123"
}
```

**Response (Success - 201):**
```json
{
    "message": "User registered successfully!",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "0812345678"
    }
}
```

**Response (Error - 400):**
```json
{
    "error": "Error message here"
}
```

---

## 3. User Login
```http
POST /api/auth/login/
```

**Headers:**
```
Content-Type: application/json
X-CSRFToken: <csrf_token_from_step_1>
```

**Request Body:**
```json
{
    "email": "john@example.com",
    "password": "secure_password123"
}
```

**Response (Success - 200):**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response Headers:**
```
Set-Cookie: access=<access_token>; HttpOnly; Secure; SameSite=None
Set-Cookie: refresh=<refresh_token>; HttpOnly; Secure; SameSite=None
X-CSRFToken: <new_csrf_token>
```

**Response (Error - 401):**
```json
{
    "detail": "Email or Password is incorrect!"
}
```

---

## 4. Get User Profile
```http
GET /api/auth/user/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Response (Success - 200):**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
}
```

**Response (Error - 401):**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

---

## 5. Refresh Token
```http
POST /api/auth/refresh-token/
```

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{}
```

**Response (Success - 200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response Headers:**
```
Set-Cookie: refresh=<new_refresh_token>; HttpOnly; Secure; SameSite=None
X-CSRFToken: <csrf_token>
```

---

## 6. Logout
```http
POST /api/auth/logout/
```

**Headers:**
```
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>
```

**Request Body:**
```json
{}
```

**Response (Success - 200):**
```json
{}
```

**Response Headers:**
```
Set-Cookie: access=; expires=Thu, 01 Jan 1970 00:00:00 GMT
Set-Cookie: refresh=; expires=Thu, 01 Jan 1970 00:00:00 GMT
Set-Cookie: X-CSRFToken=; expires=Thu, 01 Jan 1970 00:00:00 GMT
Set-Cookie: csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT
```

---

## JavaScript Implementation Example

```javascript
class AuthAPI {
    constructor(baseURL = 'https://olaf-backend.onrender.com/api/auth') {
        this.baseURL = baseURL;
        this.csrfToken = null;
    }

    // 1. Get CSRF Token
    async getCSRFToken() {
        const response = await fetch(`${this.baseURL}/csrf/`, {
            method: 'GET',
            credentials: 'include'
        });
        
        this.csrfToken = response.headers.get('X-CSRFToken');
        return this.csrfToken;
    }

    // 2. Register
    async register(userData) {
        const response = await fetch(`${this.baseURL}/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(userData)
        });
        
        return await response.json();
    }

    // 3. Login
    async login(email, password) {
        // Get CSRF token first
        await this.getCSRFToken();
        
        const response = await fetch(`${this.baseURL}/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        // Update CSRF token from response
        this.csrfToken = response.headers.get('X-CSRFToken');
        
        return data;
    }

    // 4. Get User Profile
    async getUserProfile() {
        const response = await fetch(`${this.baseURL}/user/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${this.getAccessToken()}`,
                'X-CSRFToken': this.csrfToken
            },
            credentials: 'include'
        });
        
        return await response.json();
    }

    // 5. Refresh Token
    async refreshToken() {
        const response = await fetch(`${this.baseURL}/refresh-token/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({})
        });
        
        this.csrfToken = response.headers.get('X-CSRFToken');
        return await response.json();
    }

    // 6. Logout
    async logout() {
        const response = await fetch(`${this.baseURL}/logout/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.getAccessToken()}`,
                'X-CSRFToken': this.csrfToken
            },
            credentials: 'include',
            body: JSON.stringify({})
        });
        
        this.csrfToken = null;
        return response.ok;
    }

    // Helper: Get access token from cookie
    getAccessToken() {
        const cookies = document.cookie.split(';');
        const accessCookie = cookies.find(cookie => 
            cookie.trim().startsWith('access=')
        );
        return accessCookie ? accessCookie.split('=')[1] : null;
    }
}

// Usage Example
const authAPI = new AuthAPI();

// Register
const registerData = {
    username: 'john_doe',
    email: 'john@example.com',
    first_name: 'John',
    last_name: 'Doe',
    phone: '0812345678',
    password: 'secure_password123',
    password2: 'secure_password123'
};

authAPI.register(registerData)
    .then(result => console.log('Register:', result))
    .catch(error => console.error('Register Error:', error));

// Login
authAPI.login('john@example.com', 'secure_password123')
    .then(result => console.log('Login:', result))
    .catch(error => console.error('Login Error:', error));

// Get User Profile
authAPI.getUserProfile()
    .then(result => console.log('User Profile:', result))
    .catch(error => console.error('Profile Error:', error));
```

## Important Notes

1. **Credentials: 'include'** - ต้องใช้ในทุก request เพื่อให้ cookies ถูกส่งและรับ
2. **CSRF Token** - ต้องขอใหม่ก่อน login และใช้ในทุก authenticated request
3. **Access Token** - เก็บใน HttpOnly cookie อัตโนมัติ ไม่ต้องจัดการเอง
4. **Error Handling** - ควรจัดการ error cases อย่างเหมาะสม
5. **Token Refresh** - ควรทำอัตโนมัติเมื่อ access token หมดอายุ
