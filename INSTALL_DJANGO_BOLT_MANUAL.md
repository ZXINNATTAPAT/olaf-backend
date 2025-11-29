# ติดตั้ง Django-Bolt แบบ Manual (แก้ปัญหา Network)

เนื่องจากมีปัญหา network connection ในการ clone จาก GitHub ให้ใช้วิธีนี้แทน:

## ขั้นตอนที่ 1: Clone Manual (ลองหลายครั้งถ้า timeout)

```bash
# ไปที่โฟลเดอร์ชั่วคราว
cd /tmp

# ลบโฟลเดอร์เก่า (ถ้ามี)
rm -rf django-bolt

# Clone repository (ลองหลายครั้งถ้า timeout)
git clone https://github.com/FarhanAliRaza/django-bolt.git
cd django-bolt

# Checkout version ที่ต้องการ
git checkout v0.3.7

# ตรวจสอบว่า checkout สำเร็จ
git log --oneline -1
```

## ขั้นตอนที่ 2: Install จาก Local Directory

```bash
# กลับไปที่ project directory
cd /Users/zxin/Documents/ZXIN/1_PERSONAL/MYPJ/SOFTTEST/olaf-backend

# เปิดใช้งาน virtual environment (Python 3.10+)
source venv/bin/activate

# ตรวจสอบ Python version (ต้อง >= 3.10)
python --version

# Install จาก local directory
pip install /tmp/django-bolt

# หรือถ้าต้องการ editable install
pip install -e /tmp/django-bolt
```

## ทางเลือก: Download ZIP

ถ้า git clone ยังมีปัญหา ให้ใช้วิธีนี้:

```bash
# 1. Download ZIP
cd /tmp
curl -L https://github.com/FarhanAliRaza/django-bolt/archive/refs/tags/v0.3.7.zip -o django-bolt.zip

# 2. Extract
unzip django-bolt.zip
cd django-bolt-0.3.7

# 3. Install
cd /Users/zxin/Documents/ZXIN/1_PERSONAL/MYPJ/SOFTTEST/olaf-backend
source venv/bin/activate
pip install /tmp/django-bolt-0.3.7
```

## ตรวจสอบการติดตั้ง

```bash
python -c "import django_bolt; print('Django-Bolt installed successfully!')"
python -c "import django_bolt; print(django_bolt.__version__)"
```

## หมายเหตุ

- ต้องมี Python >= 3.10
- ต้องมี Rust toolchain (rustc, cargo) และ maturin
- การ build ครั้งแรกอาจใช้เวลานาน (5-10 นาที)

