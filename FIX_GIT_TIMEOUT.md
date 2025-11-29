# แก้ไขปัญหา Git Clone Timeout

## วิธีที่ 1: Clone Manual แล้ว Install จาก Local (แนะนำ)

```bash
# 1. Clone repository ไปยังโฟลเดอร์ชั่วคราว
cd /tmp
git clone https://github.com/FarhanAliRaza/django-bolt.git
cd django-bolt
git checkout v0.3.7

# 2. Install จาก local directory
cd /Users/zxin/Documents/ZXIN/1_PERSONAL/MYPJ/SOFTTEST/olaf-backend
source venv/bin/activate
pip3 install /tmp/django-bolt
```

## วิธีที่ 2: ใช้ SSH แทน HTTPS

```bash
# ตั้งค่า SSH key สำหรับ GitHub ก่อน (ถ้ายังไม่มี)
# แล้วใช้:
pip3 install git+ssh://git@github.com/FarhanAliRaza/django-bolt.git@v0.3.7
```

## วิธีที่ 3: เพิ่ม Timeout และ Retry

```bash
# ตั้งค่า git timeout
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

# ลองใหม่
pip3 install git+https://github.com/FarhanAliRaza/django-bolt.git@v0.3.7
```

## วิธีที่ 4: ใช้ Proxy หรือ Mirror

```bash
# ถ้ามี proxy
export http_proxy=http://proxy.example.com:8080
export https_proxy=http://proxy.example.com:8080

# หรือใช้ GitHub mirror
pip3 install git+https://ghproxy.com/https://github.com/FarhanAliRaza/django-bolt.git@v0.3.7
```

## วิธีที่ 5: Download ZIP แล้ว Install

```bash
# 1. Download ZIP จาก GitHub
cd /tmp
curl -L https://github.com/FarhanAliRaza/django-bolt/archive/refs/tags/v0.3.7.zip -o django-bolt.zip
unzip django-bolt.zip
cd django-bolt-0.3.7

# 2. Install
cd /Users/zxin/Documents/ZXIN/1_PERSONAL/MYPJ/SOFTTEST/olaf-backend
source venv/bin/activate
pip3 install /tmp/django-bolt-0.3.7
```

## วิธีที่ 6: ตรวจสอบ Network Connection

```bash
# ตรวจสอบว่าเข้าถึง GitHub ได้
ping github.com
curl -I https://github.com

# ตรวจสอบ DNS
nslookup github.com
```

