# การติดตั้ง Django-Bolt

Django-Bolt ต้อง build จาก source เพราะมี Rust components

## ความต้องการระบบ

1. **Python >= 3.10** (อัปเดต runtime.txt แล้ว)
2. **Rust toolchain** (rustc, cargo)
3. **maturin** (Python package สำหรับ build Rust extensions)

## ขั้นตอนการติดตั้ง

### 1. ติดตั้ง Rust (ถ้ายังไม่มี)

```bash
# macOS
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# หรือใช้ Homebrew
brew install rust

# ตรวจสอบการติดตั้ง
rustc --version
cargo --version
```

### 2. ติดตั้ง maturin

```bash
pip install maturin
```

### 3. ติดตั้ง Django-Bolt

#### วิธีที่ 1: ติดตั้งจาก GitHub (แนะนำ)

```bash
pip install git+https://github.com/FarhanAliRaza/django-bolt.git@v0.3.7
```

#### วิธีที่ 2: Clone และ build จาก source

```bash
git clone https://github.com/FarhanAliRaza/django-bolt.git
cd django-bolt
pip install -e .
```

### 4. ตรวจสอบการติดตั้ง

```bash
python -c "import django_bolt; print(django_bolt.__version__)"
```

## หมายเหตุ

- การ build ครั้งแรกอาจใช้เวลานาน (5-10 นาที) เพราะต้อง compile Rust code
- ต้องมี internet connection สำหรับ download Rust dependencies
- บน macOS อาจต้องติดตั้ง Xcode Command Line Tools:
  ```bash
  xcode-select --install
  ```

## Troubleshooting

### Error: "maturin not found"
```bash
pip install maturin
```

### Error: "rustc not found"
ติดตั้ง Rust toolchain ตามขั้นตอนที่ 1

### Error: "Python version too old"
อัปเดต Python เป็น 3.10+ หรือใช้ pyenv:
```bash
pyenv install 3.10.0
pyenv local 3.10.0
```

### Error: "Failed to build"
ตรวจสอบว่า:
- Rust toolchain ติดตั้งถูกต้อง
- Python version >= 3.10
- มี Xcode Command Line Tools (macOS)

