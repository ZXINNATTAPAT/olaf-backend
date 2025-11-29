# แก้ไขปัญหา Homebrew LLVM Download Error

## วิธีที่ 1: ล้าง Homebrew Cache และลองใหม่

```bash
# ล้าง cache
brew cleanup --prune=all

# ลองติดตั้ง Rust อีกครั้ง
brew install rust
```

## วิธีที่ 2: ติดตั้ง Rust โดยตรง (ไม่ผ่าน Homebrew)

```bash
# ติดตั้ง Rust โดยตรงจาก rustup (แนะนำ)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# ตามด้วย
source $HOME/.cargo/env

# ตรวจสอบ
rustc --version
cargo --version
```

## วิธีที่ 3: แก้ไข Homebrew Repository

```bash
# เปลี่ยน mirror (ถ้า network มีปัญหา)
export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles

# หรือ reset Homebrew
cd $(brew --repository)
git remote set-url origin https://github.com/Homebrew/brew.git
cd $(brew --repository homebrew/core)
git remote set-url origin https://github.com/Homebrew/homebrew-core.git

# ลองใหม่
brew update
brew install rust
```

## วิธีที่ 4: ติดตั้ง LLVM แยกก่อน

```bash
# ลองติดตั้ง LLVM แยก
brew install llvm

# ถ้ายังไม่ได้ ลอง force reinstall
brew reinstall llvm

# หรือติดตั้งจาก source (ช้ากว่าแต่เสถียรกว่า)
brew install --build-from-source llvm
```

## วิธีที่ 5: ข้าม LLVM และใช้ Rustup โดยตรง (แนะนำที่สุด)

```bash
# ติดตั้ง Rust โดยตรง (ไม่ต้องใช้ Homebrew)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# เพิ่ม Rust ไปยัง PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# ตรวจสอบ
rustc --version
cargo --version

# ติดตั้ง maturin
pip install maturin

# ติดตั้ง Django-Bolt
pip install git+https://github.com/FarhanAliRaza/django-bolt.git@v0.3.7
```

## วิธีที่ 6: ใช้ Docker หรือ Virtual Environment

ถ้ายังมีปัญหา อาจใช้ Docker หรือ build ใน environment อื่น

## ตรวจสอบ Network

```bash
# ตรวจสอบว่าเข้าถึง GitHub ได้
curl -I https://github.com

# ตรวจสอบ Homebrew
brew doctor
```

