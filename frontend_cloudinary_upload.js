// Frontend Cloudinary Upload Helper
// This script handles direct upload to Cloudinary from frontend

class CloudinaryUploader {
    constructor(cloudName, uploadPreset) {
        this.cloudName = cloudName;
        this.uploadPreset = uploadPreset;
        this.uploadUrl = `https://api.cloudinary.com/v1_1/${cloudName}/image/upload`;
    }

    // Upload single image to Cloudinary
    async uploadImage(file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('upload_preset', this.uploadPreset);
        formData.append('folder', options.folder || 'shared/images');
        
        // Add transformation options
        if (options.width) formData.append('width', options.width);
        if (options.height) formData.append('height', options.height);
        if (options.crop) formData.append('crop', options.crop);
        if (options.quality) formData.append('quality', options.quality);
        if (options.format) formData.append('format', options.format);

        try {
            const response = await fetch(this.uploadUrl, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const result = await response.json();
            return {
                success: true,
                data: {
                    public_id: result.public_id,
                    secure_url: result.secure_url,
                    url: result.url,
                    width: result.width,
                    height: result.height,
                    format: result.format,
                    bytes: result.bytes
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Upload multiple images
    async uploadMultipleImages(files, options = {}) {
        const uploadPromises = files.map(file => this.uploadImage(file, options));
        const results = await Promise.all(uploadPromises);
        
        return {
            success: results.every(r => r.success),
            results: results
        };
    }
}

// API Helper for Backend Communication
class SharedImagesAPI {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.token = token;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    // Add image path to blog post
    async addImageToPost(postId, imageData, options = {}) {
        const payload = {
            image: imageData.secure_url,
            caption: options.caption || '',
            is_primary: options.isPrimary || false,
            sort_order: options.sortOrder || 0
        };

        try {
            const response = await fetch(`${this.baseUrl}/api/posts/${postId}/add-image-path/`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error adding image to post:', error);
            throw error;
        }
    }

    // Add image path to CloudDiary
    async addImageToCloudDiary(cloudDiaryId, imageData, options = {}) {
        const payload = {
            image: imageData.secure_url,
            caption: options.caption || '',
            is_primary: options.isPrimary || false,
            sort_order: options.sortOrder || 0
        };

        try {
            const response = await fetch(`${this.baseUrl}/api/clouddiary/${cloudDiaryId}/add-image-path/`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error adding image to CloudDiary:', error);
            throw error;
        }
    }

    // Get images for post
    async getPostImages(postId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/posts/${postId}/images/`, {
                method: 'GET',
                headers: this.headers
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting post images:', error);
            throw error;
        }
    }

    // Get images for CloudDiary
    async getCloudDiaryImages(cloudDiaryId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/clouddiary/${cloudDiaryId}/shared-images/`, {
                method: 'GET',
                headers: this.headers
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting CloudDiary images:', error);
            throw error;
        }
    }

    // Set primary image
    async setPrimaryImage(imageId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/images/${imageId}/set-primary/`, {
                method: 'PATCH',
                headers: this.headers
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error setting primary image:', error);
            throw error;
        }
    }

    // Delete image
    async deleteImage(imageId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/images/${imageId}/delete/`, {
                method: 'DELETE',
                headers: this.headers
            });

            return response.status === 204;
        } catch (error) {
            console.error('Error deleting image:', error);
            throw error;
        }
    }
}

// Complete Image Upload Manager
class ImageUploadManager {
    constructor(cloudName, uploadPreset, apiBaseUrl, token) {
        this.cloudinary = new CloudinaryUploader(cloudName, uploadPreset);
        this.api = new SharedImagesAPI(apiBaseUrl, token);
    }

    // Upload and save to blog post
    async uploadToPost(postId, file, options = {}) {
        // 1. Upload to Cloudinary
        const uploadResult = await this.cloudinary.uploadImage(file, {
            folder: 'shared/images',
            quality: 'auto',
            format: 'auto'
        });

        if (!uploadResult.success) {
            throw new Error(`Cloudinary upload failed: ${uploadResult.error}`);
        }

        // 2. Save to backend
        const saveResult = await this.api.addImageToPost(postId, uploadResult.data, options);
        
        return {
            cloudinary: uploadResult.data,
            backend: saveResult
        };
    }

    // Upload and save to CloudDiary
    async uploadToCloudDiary(cloudDiaryId, file, options = {}) {
        // 1. Upload to Cloudinary
        const uploadResult = await this.cloudinary.uploadImage(file, {
            folder: 'shared/images',
            quality: 'auto',
            format: 'auto'
        });

        if (!uploadResult.success) {
            throw new Error(`Cloudinary upload failed: ${uploadResult.error}`);
        }

        // 2. Save to backend
        const saveResult = await this.api.addImageToCloudDiary(cloudDiaryId, uploadResult.data, options);
        
        return {
            cloudinary: uploadResult.data,
            backend: saveResult
        };
    }

    // Upload multiple images to post
    async uploadMultipleToPost(postId, files, options = {}) {
        const results = [];
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const fileOptions = {
                ...options,
                isPrimary: i === 0, // First image is primary
                sortOrder: i
            };
            
            try {
                const result = await this.uploadToPost(postId, file, fileOptions);
                results.push({ success: true, result });
            } catch (error) {
                results.push({ success: false, error: error.message });
            }
        }
        
        return results;
    }
}

// Usage Examples
const imageManager = new ImageUploadManager(
    'your-cloud-name',           // Cloudinary cloud name
    'your-upload-preset',        // Cloudinary upload preset
    'https://olaf-backend.onrender.com',  // Your API base URL
    'your-jwt-token'             // Your JWT token
);

// Example 1: Upload single image to blog post
async function uploadBlogImage() {
    const fileInput = document.getElementById('blogImageFile');
    const file = fileInput.files[0];
    
    if (file) {
        try {
            const result = await imageManager.uploadToPost(4, file, {
                caption: 'My blog image',
                isPrimary: true,
                sortOrder: 0
            });
            console.log('Upload successful:', result);
        } catch (error) {
            console.error('Upload failed:', error);
        }
    }
}

// Example 2: Upload multiple images
async function uploadMultipleBlogImages() {
    const fileInput = document.getElementById('multipleBlogImages');
    const files = Array.from(fileInput.files);
    
    if (files.length > 0) {
        try {
            const results = await imageManager.uploadMultipleToPost(4, files, {
                caption: 'Blog images'
            });
            console.log('Multiple upload results:', results);
        } catch (error) {
            console.error('Multiple upload failed:', error);
        }
    }
}

// Example 3: Upload to CloudDiary
async function uploadDiaryImage() {
    const fileInput = document.getElementById('diaryImageFile');
    const file = fileInput.files[0];
    
    if (file) {
        try {
            const result = await imageManager.uploadToCloudDiary(1, file, {
                caption: 'My diary photo',
                isPrimary: true,
                sortOrder: 0
            });
            console.log('Diary upload successful:', result);
        } catch (error) {
            console.error('Diary upload failed:', error);
        }
    }
}

// HTML Form Example
const htmlForm = `
<div>
    <h3>Upload to Blog Post</h3>
    <input type="file" id="blogImageFile" accept="image/*" multiple>
    <input type="text" id="blogCaption" placeholder="Image caption">
    <input type="checkbox" id="blogIsPrimary"> Set as primary
    <button onclick="uploadBlogImage()">Upload to Post</button>
</div>

<div>
    <h3>Upload Multiple Images</h3>
    <input type="file" id="multipleBlogImages" accept="image/*" multiple>
    <button onclick="uploadMultipleBlogImages()">Upload Multiple</button>
</div>

<div>
    <h3>Upload to CloudDiary</h3>
    <input type="file" id="diaryImageFile" accept="image/*">
    <input type="text" id="diaryCaption" placeholder="Diary image caption">
    <input type="checkbox" id="diaryIsPrimary"> Set as primary
    <button onclick="uploadDiaryImage()">Upload to Diary</button>
</div>
`;

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CloudinaryUploader, SharedImagesAPI, ImageUploadManager };
}
