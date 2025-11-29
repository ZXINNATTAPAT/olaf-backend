# อัปเดต Python เป็น 3.10+

django-bolt ต้องการ Python >= 3.10 แต่ตอนนี้ใช้ Python 3.9.6

## วิธีที่ 1: ติดตั้ง Python 3.10+ ผ่าน Homebrew (แนะนำ)

```bash
# 1. ติดตั้ง Python 3.10
brew install python@3.10

# 2. ตรวจสอบ path
which python3.10

# 3. สร้าง virtual environment ใหม่ด้วย Python 3.10
cd /Users/zxin/Documents/ZXIN/1_PERSONAL/MYPJ/SOFTTEST/olaf-backend
deactivate  # ถ้ายังอยู่ใน venv เก่า
rm -rf venv  # ลบ venv เก่า
python3.10 -m venv venv

# 4. เปิดใช้งาน venv ใหม่
source venv/bin/activate

# 5. ตรวจสอบ version
python --version  # ควรเป็น 3.10.x

# 6. ติดตั้ง dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## วิธีที่ 2: ใช้ pyenv (สำหรับจัดการหลาย Python versions)

```bash
# 1. ติดตั้ง pyenv
brew install pyenv

# 2. เพิ่ม pyenv ไปยัง shell config
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# 3. ติดตั้ง Python 3.10
pyenv install 3.10.12

# 4. ตั้งค่า local Python version
cd /Users/zxin/Documents/ZXIN/1_PERSONAL/MYPJ/SOFTTEST/olaf-backend
pyenv local 3.10.12

# 5. สร้าง virtual environment ใหม่
rm -rf venv
python -m venv venv
source venv/bin/activate

# 6. ตรวจสอบ version
python --version  # ควรเป็น 3.10.12

# 7. ติดตั้ง dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## วิธีที่ 3: Download Python จาก python.org

```bash
# 1. Download Python 3.10+ จาก https://www.python.org/downloads/
# 2. ติดตั้งตามปกติ
# 3. ใช้ python3.10 แทน python3
python3.10 -m venv venv
source venv/bin/activate
```

## วิธีที่ 4: ใช้ Django REST Framework ต่อไปก่อน (ไม่ต้องอัปเดต Python)

ถ้าไม่ต้องการอัปเดต Python ตอนนี้ สามารถ:

1. ใช้ Django REST Framework ต่อไปก่อน
2. Migrate ไป Django-Bolt ทีหลังเมื่อพร้อมอัปเดต Python

## ตรวจสอบหลังอัปเดต

```bash
# ตรวจสอบ Python version
python --version  # ควรเป็น 3.10.x หรือสูงกว่า

# ตรวจสอบ pip
pip --version

# ทดสอบติดตั้ง django-bolt
pip install git+https://github.com/FarhanAliRaza/django-bolt.git@v0.3.7
```
