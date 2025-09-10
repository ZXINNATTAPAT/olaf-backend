#!/bin/bash

# Test commands for Shared Images API
# Replace YOUR_JWT_TOKEN with actual token

BASE_URL="https://olaf-backend.onrender.com"
# BASE_URL="http://localhost:8000"  # For local testing

JWT_TOKEN="YOUR_JWT_TOKEN_HERE"

echo "=== Testing Shared Images API ==="

# 1. Test authentication - Get posts
echo "1. Testing authentication..."
curl -X GET \
  "$BASE_URL/api/posts/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\n"

# 2. Test image upload to post
echo "2. Testing image upload to post..."
curl -X POST \
  "$BASE_URL/api/posts/4/upload-image/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "image=@test_image.jpg" \
  -F "caption=Test image upload" \
  -F "is_primary=true" \
  -F "sort_order=0"

echo -e "\n\n"

# 3. Test get images for post
echo "3. Testing get images for post..."
curl -X GET \
  "$BASE_URL/api/posts/4/images/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\n"

# 4. Test get primary image
echo "4. Testing get primary image..."
curl -X GET \
  "$BASE_URL/api/posts/4/primary-image/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\n"

# 5. Test CloudDiary image upload
echo "5. Testing CloudDiary image upload..."
curl -X POST \
  "$BASE_URL/api/clouddiary/1/upload-shared-image/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "image=@test_image.jpg" \
  -F "caption=CloudDiary image" \
  -F "is_primary=true" \
  -F "sort_order=0"

echo -e "\n\n"

# 6. Test get CloudDiary shared images
echo "6. Testing get CloudDiary shared images..."
curl -X GET \
  "$BASE_URL/api/clouddiary/1/shared-images/" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\n=== Test Complete ==="
