#!/bin/bash

# Test create post with image endpoint
BASE_URL="https://olaf-backend.onrender.com"
# BASE_URL="http://localhost:8000"  # For local testing

JWT_TOKEN="YOUR_JWT_TOKEN_HERE"

echo "=== Testing Create Post with Image ==="

# Test 1: Create post without image
echo "1. Testing create post without image..."
curl -X POST \
  "$BASE_URL/api/posts/create-with-image/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "header": "Test Post",
    "short": "Test Description",
    "post_text": "This is a test post",
    "user_id": 1
  }'

echo -e "\n\n"

# Test 2: Create post with image
echo "2. Testing create post with image..."
curl -X POST \
  "$BASE_URL/api/posts/create-with-image/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "header": "Test Post with Image",
    "short": "Test Description with Image",
    "post_text": "This is a test post with image",
    "user_id": 1,
    "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/test.jpg",
    "caption": "Test image",
    "is_primary": true,
    "sort_order": 0
  }'

echo -e "\n\n"

# Test 3: Check if endpoint exists
echo "3. Testing OPTIONS request..."
curl -X OPTIONS \
  "$BASE_URL/api/posts/create-with-image/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\n=== Test Complete ==="
