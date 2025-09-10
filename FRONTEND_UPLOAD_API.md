# Frontend Upload API Documentation

## Overview
ระบบใหม่ที่ให้ frontend อัปโหลดรูปภาพไปยัง Cloudinary โดยตรง แล้วส่งแค่ path/URL กลับมาให้ backend เก็บไว้

## Workflow
1. **Frontend** อัปโหลดรูปภาพไปยัง Cloudinary โดยตรง
2. **Frontend** ส่ง image URL กลับมาให้ backend
3. **Backend** เก็บ image URL และ metadata ไว้ในฐานข้อมูล

## Frontend Configuration

### Cloudinary Setup
```javascript
const cloudinaryConfig = {
    cloudName: 'your-cloud-name',
    uploadPreset: 'your-upload-preset',  // ต้องตั้งค่าใน Cloudinary Dashboard
    uploadUrl: 'https://api.cloudinary.com/v1_1/your-cloud-name/image/upload'
};
```

### Upload Preset Configuration
ใน Cloudinary Dashboard:
1. ไปที่ Settings > Upload
2. สร้าง Upload Preset ใหม่
3. ตั้งค่า:
   - **Signing Mode**: Unsigned
   - **Folder**: shared/images
   - **Quality**: Auto
   - **Format**: Auto

## API Endpoints

### 1. Blog Posts

#### Add Image Path to Post
```
POST /api/posts/{post_id}/add-image-path/
```
**Request Body:**
```json
{
    "image": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/shared/images/abc123.jpg",
    "caption": "Image caption",
    "is_primary": true,
    "sort_order": 0
}
```

#### Get All Images for Post
```
GET /api/posts/{post_id}/images/
```

#### Get Primary Image for Post
```
GET /api/posts/{post_id}/primary-image/
```

#### Set Primary Image
```
PATCH /api/images/{image_id}/set-primary/
```

#### Delete Image
```
DELETE /api/images/{image_id}/delete/
```

### 2. CloudDiary

#### Add Image Path to CloudDiary
```
POST /api/clouddiary/{clouddiary_id}/add-image-path/
```
**Request Body:**
```json
{
    "image": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/shared/images/def456.jpg",
    "caption": "Diary image caption",
    "is_primary": true,
    "sort_order": 0
}
```

#### Get All Shared Images for CloudDiary
```
GET /api/clouddiary/{clouddiary_id}/shared-images/
```

#### Get Primary Shared Image for CloudDiary
```
GET /api/clouddiary/{clouddiary_id}/primary-shared-image/
```

## Frontend Implementation

### 1. Basic Upload to Cloudinary
```javascript
async function uploadToCloudinary(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', 'your-upload-preset');
    formData.append('folder', 'shared/images');
    
    const response = await fetch('https://api.cloudinary.com/v1_1/your-cloud-name/image/upload', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}
```

### 2. Complete Upload Flow
```javascript
async function uploadImageToPost(postId, file, options = {}) {
    // Step 1: Upload to Cloudinary
    const cloudinaryResult = await uploadToCloudinary(file);
    
    // Step 2: Save to backend
    const response = await fetch(`/api/posts/${postId}/add-image-path/`, {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            image: cloudinaryResult.secure_url,
            caption: options.caption || '',
            is_primary: options.isPrimary || false,
            sort_order: options.sortOrder || 0
        })
    });
    
    return await response.json();
}
```

### 3. Using the Helper Class
```javascript
// Initialize
const imageManager = new ImageUploadManager(
    'your-cloud-name',
    'your-upload-preset',
    'https://olaf-backend.onrender.com',
    'your-jwt-token'
);

// Upload single image
const result = await imageManager.uploadToPost(4, file, {
    caption: 'My blog image',
    isPrimary: true,
    sortOrder: 0
});

// Upload multiple images
const results = await imageManager.uploadMultipleToPost(4, files, {
    caption: 'Blog images'
});
```

## Response Format

### Cloudinary Upload Response
```json
{
    "public_id": "shared/images/abc123",
    "secure_url": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/shared/images/abc123.jpg",
    "url": "http://res.cloudinary.com/your-cloud/image/upload/v1234567890/shared/images/abc123.jpg",
    "width": 1920,
    "height": 1080,
    "format": "jpg",
    "bytes": 245760
}
```

### Backend Save Response
```json
{
    "id": 1,
    "image": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/shared/images/abc123.jpg",
    "caption": "My blog image",
    "image_url": "http://res.cloudinary.com/your-cloud/image/upload/v1234567890/shared/images/abc123.jpg",
    "image_public_id": "shared/images/abc123",
    "image_secure_url": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/shared/images/abc123.jpg",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "is_primary": true,
    "sort_order": 0
}
```

## HTML Form Example
```html
<!DOCTYPE html>
<html>
<head>
    <title>Image Upload Test</title>
</head>
<body>
    <h2>Upload to Blog Post</h2>
    <form id="blogUploadForm">
        <input type="file" id="blogImageFile" accept="image/*" multiple>
        <input type="text" id="blogCaption" placeholder="Image caption">
        <input type="checkbox" id="blogIsPrimary"> Set as primary
        <input type="number" id="blogSortOrder" value="0" min="0">
        <button type="button" onclick="uploadBlogImage()">Upload to Post</button>
    </form>

    <h2>Upload to CloudDiary</h2>
    <form id="diaryUploadForm">
        <input type="file" id="diaryImageFile" accept="image/*" multiple>
        <input type="text" id="diaryCaption" placeholder="Diary image caption">
        <input type="checkbox" id="diaryIsPrimary"> Set as primary
        <input type="number" id="diarySortOrder" value="0" min="0">
        <button type="button" onclick="uploadDiaryImage()">Upload to Diary</button>
    </form>

    <script src="frontend_cloudinary_upload.js"></script>
    <script>
        // Initialize image manager
        const imageManager = new ImageUploadManager(
            'your-cloud-name',
            'your-upload-preset',
            'https://olaf-backend.onrender.com',
            'your-jwt-token'
        );

        async function uploadBlogImage() {
            const fileInput = document.getElementById('blogImageFile');
            const file = fileInput.files[0];
            const caption = document.getElementById('blogCaption').value;
            const isPrimary = document.getElementById('blogIsPrimary').checked;
            const sortOrder = parseInt(document.getElementById('blogSortOrder').value);

            if (file) {
                try {
                    const result = await imageManager.uploadToPost(4, file, {
                        caption,
                        isPrimary,
                        sortOrder
                    });
                    console.log('Upload successful:', result);
                    alert('Image uploaded successfully!');
                } catch (error) {
                    console.error('Upload failed:', error);
                    alert('Upload failed: ' + error.message);
                }
            }
        }

        async function uploadDiaryImage() {
            const fileInput = document.getElementById('diaryImageFile');
            const file = fileInput.files[0];
            const caption = document.getElementById('diaryCaption').value;
            const isPrimary = document.getElementById('diaryIsPrimary').checked;
            const sortOrder = parseInt(document.getElementById('diarySortOrder').value);

            if (file) {
                try {
                    const result = await imageManager.uploadToCloudDiary(1, file, {
                        caption,
                        isPrimary,
                        sortOrder
                    });
                    console.log('Diary upload successful:', result);
                    alert('Diary image uploaded successfully!');
                } catch (error) {
                    console.error('Diary upload failed:', error);
                    alert('Diary upload failed: ' + error.message);
                }
            }
        }
    </script>
</body>
</html>
```

## Advantages of This Approach

1. **Faster Upload**: Frontend uploads directly to Cloudinary
2. **Reduced Server Load**: Backend only stores metadata
3. **Better User Experience**: No timeout issues with large files
4. **Scalability**: Cloudinary handles CDN and optimization
5. **Cost Effective**: Reduced bandwidth usage on your server

## Security Considerations

1. **Upload Preset**: Use unsigned upload presets with restrictions
2. **File Validation**: Validate file types and sizes on frontend
3. **Authentication**: Always verify JWT token before saving to backend
4. **CORS**: Configure CORS properly for your domain

## Error Handling

```javascript
try {
    const result = await imageManager.uploadToPost(postId, file, options);
    // Handle success
} catch (error) {
    if (error.message.includes('Cloudinary upload failed')) {
        // Handle Cloudinary upload error
    } else if (error.message.includes('HTTP error')) {
        // Handle backend API error
    } else {
        // Handle other errors
    }
}
```
