#!/bin/bash

# Test JSON upload to backend
# This tests the corrected API endpoints that accept JSON

BASE_URL="https://olaf-backend.onrender.com"
JWT_TOKEN="YOUR_JWT_TOKEN_HERE"

echo "=== Testing JSON Upload API ==="
echo ""

# 1. Test add image path to blog post
echo "1. Testing add image path to blog post..."
curl -X POST \
  "$BASE_URL/api/posts/4/add-image-path/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://res.cloudinary.com/dm02oprw0/image/upload/v1757496777/olaf-posts/post_1757496743339_bbl07btam.png",
    "caption": "Test image from frontend upload",
    "is_primary": true,
    "sort_order": 0
  }'

echo -e "\n\n"

# 2. Test add image path to CloudDiary
echo "2. Testing add image path to CloudDiary..."
curl -X POST \
  "$BASE_URL/api/clouddiary/1/add-image-path/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://res.cloudinary.com/dm02oprw0/image/upload/v1757496777/olaf-posts/post_1757496743339_bbl07btam.png",
    "caption": "Test diary image from frontend upload",
    "is_primary": true,
    "sort_order": 0
  }'

echo -e "\n\n"

# 3. Test get images for post
echo "3. Testing get images for post..."
curl -X GET \
  "$BASE_URL/api/posts/4/images/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\n"

# 4. Test get images for CloudDiary
echo "4. Testing get images for CloudDiary..."
curl -X GET \
  "$BASE_URL/api/clouddiary/1/shared-images/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\n=== Test Complete ==="
