#!/bin/bash

# Test commands for Frontend Upload API
# This tests the new approach where frontend uploads to Cloudinary first

BASE_URL="https://olaf-backend.onrender.com"
# BASE_URL="http://localhost:8000"  # For local testing

JWT_TOKEN="YOUR_JWT_TOKEN_HERE"

echo "=== Testing Frontend Upload API ==="
echo "Note: This tests the new approach where frontend uploads to Cloudinary first"
echo ""

# 1. Test authentication - Get posts
echo "1. Testing authentication..."
curl -X GET \
  "$BASE_URL/api/posts/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\n"

# 2. Test adding image path to blog post
echo "2. Testing add image path to blog post..."
curl -X POST \
  "$BASE_URL/api/posts/4/add-image-path/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/shared/images/test123.jpg",
    "caption": "Test image from frontend upload",
    "is_primary": true,
    "sort_order": 0
  }'

echo -e "\n\n"

# 3. Test adding image path to CloudDiary
echo "3. Testing add image path to CloudDiary..."
curl -X POST \
  "$BASE_URL/api/clouddiary/1/add-image-path/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/shared/images/test456.jpg",
    "caption": "Test diary image from frontend upload",
    "is_primary": true,
    "sort_order": 0
  }'

echo -e "\n\n"

# 4. Test get images for post
echo "4. Testing get images for post..."
curl -X GET \
  "$BASE_URL/api/posts/4/images/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\n"

# 5. Test get images for CloudDiary
echo "5. Testing get images for CloudDiary..."
curl -X GET \
  "$BASE_URL/api/clouddiary/1/shared-images/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\n"

# 6. Test set primary image
echo "6. Testing set primary image..."
curl -X PATCH \
  "$BASE_URL/api/images/1/set-primary/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\n"

# 7. Test delete image
echo "7. Testing delete image..."
curl -X DELETE \
  "$BASE_URL/api/images/1/delete/" \
  -H "Authorization: Bearer $JWT_TOKEN"

echo -e "\n\n=== Test Complete ==="
echo ""
echo "Frontend Upload Flow:"
echo "1. Frontend uploads image to Cloudinary directly"
echo "2. Frontend gets secure_url from Cloudinary response"
echo "3. Frontend sends secure_url to backend via add-image-path endpoint"
echo "4. Backend stores the URL and metadata in database"
