// Frontend JavaScript example for Shared Images API

const API_BASE_URL = 'https://olaf-backend.onrender.com';
// const API_BASE_URL = 'http://localhost:8000'; // For local testing

class SharedImagesAPI {
    constructor(token) {
        this.token = token;
        this.headers = {
            'Authorization': `Bearer ${token}`,
        };
    }

    // Upload image to blog post
    async uploadPostImage(postId, imageFile, options = {}) {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('caption', options.caption || '');
        formData.append('is_primary', options.isPrimary || false);
        formData.append('sort_order', options.sortOrder || 0);

        try {
            const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/upload-image/`, {
                method: 'POST',
                headers: this.headers,
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error uploading post image:', error);
            throw error;
        }
    }

    // Get all images for a post
    async getPostImages(postId) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/images/`, {
                method: 'GET',
                headers: {
                    ...this.headers,
                    'Content-Type': 'application/json'
                }
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

    // Get primary image for a post
    async getPostPrimaryImage(postId) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/primary-image/`, {
                method: 'GET',
                headers: {
                    ...this.headers,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting primary image:', error);
            throw error;
        }
    }

    // Set primary image
    async setPrimaryImage(imageId) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/images/${imageId}/set-primary/`, {
                method: 'PATCH',
                headers: {
                    ...this.headers,
                    'Content-Type': 'application/json'
                }
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
            const response = await fetch(`${API_BASE_URL}/api/images/${imageId}/delete/`, {
                method: 'DELETE',
                headers: this.headers
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return response.status === 204; // No content for successful deletion
        } catch (error) {
            console.error('Error deleting image:', error);
            throw error;
        }
    }

    // Upload image to CloudDiary
    async uploadCloudDiaryImage(cloudDiaryId, imageFile, options = {}) {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('caption', options.caption || '');
        formData.append('is_primary', options.isPrimary || false);
        formData.append('sort_order', options.sortOrder || 0);

        try {
            const response = await fetch(`${API_BASE_URL}/api/clouddiary/${cloudDiaryId}/upload-shared-image/`, {
                method: 'POST',
                headers: this.headers,
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error uploading CloudDiary image:', error);
            throw error;
        }
    }

    // Get CloudDiary shared images
    async getCloudDiarySharedImages(cloudDiaryId) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/clouddiary/${cloudDiaryId}/shared-images/`, {
                method: 'GET',
                headers: {
                    ...this.headers,
                    'Content-Type': 'application/json'
                }
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
}

// Usage examples
const api = new SharedImagesAPI('YOUR_JWT_TOKEN_HERE');

// Example 1: Upload image to blog post
async function uploadBlogImage() {
    const fileInput = document.getElementById('imageFile');
    const file = fileInput.files[0];
    
    if (file) {
        try {
            const result = await api.uploadPostImage(4, file, {
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

// Example 2: Get all images for a post
async function getBlogImages() {
    try {
        const images = await api.getPostImages(4);
        console.log('Post images:', images);
    } catch (error) {
        console.error('Failed to get images:', error);
    }
}

// Example 3: Upload image to CloudDiary
async function uploadDiaryImage() {
    const fileInput = document.getElementById('diaryImageFile');
    const file = fileInput.files[0];
    
    if (file) {
        try {
            const result = await api.uploadCloudDiaryImage(1, file, {
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

// HTML form example
const htmlForm = `
<form id="imageUploadForm">
    <input type="file" id="imageFile" accept="image/*" required>
    <input type="text" id="caption" placeholder="Image caption">
    <input type="checkbox" id="isPrimary"> Set as primary image
    <input type="number" id="sortOrder" value="0" min="0">
    <button type="button" onclick="uploadBlogImage()">Upload to Post</button>
</form>

<form id="diaryUploadForm">
    <input type="file" id="diaryImageFile" accept="image/*" required>
    <input type="text" id="diaryCaption" placeholder="Diary image caption">
    <input type="checkbox" id="diaryIsPrimary"> Set as primary image
    <input type="number" id="diarySortOrder" value="0" min="0">
    <button type="button" onclick="uploadDiaryImage()">Upload to Diary</button>
</form>

<button onclick="getBlogImages()">Get Post Images</button>
`;
