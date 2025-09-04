#!/bin/bash

# Start Services Script
# สคริปต์สำหรับเริ่ม services ทั้งหมด

echo "🚀 กำลังเริ่ม Services..."

# เริ่ม Redis
echo "📦 เริ่ม Redis..."
brew services start redis
sleep 2

# ตรวจสอบ Redis
echo "🔍 ตรวจสอบ Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis ทำงานแล้ว"
else
    echo "❌ Redis ไม่ทำงาน"
    exit 1
fi

# เริ่ม Django Server
echo "🐍 เริ่ม Django Server..."
python3 manage.py runserver 0.0.0.0:8000 &

# เก็บ PID ของ Django server
DJANGO_PID=$!
echo "Django PID: $DJANGO_PID"

# รอให้ server เริ่ม
sleep 3

# ตรวจสอบ Django server
echo "🔍 ตรวจสอบ Django Server..."
if curl -s http://localhost:8000/admin/ > /dev/null 2>&1; then
    echo "✅ Django Server ทำงานแล้ว"
    echo "🌐 Admin Panel: http://localhost:8000/admin/"
    echo "👤 Username: admin"
    echo "🔐 Password: admin123"
else
    echo "❌ Django Server ไม่ทำงาน"
fi

echo "🎉 Services เริ่มเสร็จสิ้น!"
echo "📝 ใช้ Ctrl+C เพื่อหยุด services"

# รอให้ user กด Ctrl+C
wait $DJANGO_PID
