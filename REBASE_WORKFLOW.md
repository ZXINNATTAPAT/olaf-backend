# Rebase Workflow Guide

## การตั้งค่า GitHub Repository สำหรับ Rebase

### 1. ตั้งค่าใน GitHub Repository

1. ไปที่ GitHub repository ของคุณ
2. คลิก **Settings** → **General**
3. เลื่อนลงไปที่ส่วน **Pull Requests**
4. ในส่วน **Merge button** ให้เลือก:
   - ✅ **Allow rebase merging**
   - ❌ **Allow merge commits** (ปิดการใช้งาน)
   - ❌ **Allow squash merging** (ปิดการใช้งาน)

### 2. ตั้งค่า Git Config

```bash
# ตั้งค่าให้ pull ใช้ rebase โดยอัตโนมัติ
git config --global pull.rebase true

# ตั้งค่าให้ rebase stash changes อัตโนมัติ
git config --global rebase.autoStash true

# ตั้งค่า push default
git config --global push.default simple
```

### 3. Rebase Workflow Commands

#### การทำงานกับ Branch ใหม่
```bash
# สร้าง branch ใหม่
git checkout -b feature/new-feature

# ทำงานและ commit
git add .
git commit -m "Add new feature"

# Push branch ใหม่
git push -u origin feature/new-feature
```

#### การ Update Branch ก่อน Push
```bash
# Switch ไป main branch
git checkout main

# Pull latest changes
git pull --rebase

# Switch กลับไป feature branch
git checkout feature/new-feature

# Rebase กับ main
git rebase main

# Push (อาจต้อง force push ถ้ามี conflict)
git push --force-with-lease
```

#### การแก้ไข Conflict ระหว่าง Rebase
```bash
# เริ่ม rebase
git rebase main

# ถ้ามี conflict
# แก้ไขไฟล์ที่มี conflict
git add <fixed-files>
git rebase --continue

# หรือยกเลิก rebase
git rebase --abort
```

### 4. Pull Request Workflow

1. **สร้าง Pull Request** จาก feature branch ไป main
2. **Review** code ใน GitHub
3. **Merge** โดยใช้ "Rebase and merge" button
4. **Delete** feature branch หลัง merge

### 5. Git Aliases ที่มีประโยชน์

```bash
# เพิ่ม aliases ใน .gitconfig
git config --global alias.rb rebase
git config --global alias.rbi "rebase --interactive"
git config --global alias.rbc "rebase --continue"
git config --global alias.rba "rebase --abort"
git config --global alias.pl "pull --rebase"
git config --global alias.lg "log --oneline --graph --decorate --all"
```

### 6. ข้อดีของ Rebase Workflow

- **Clean History**: ไม่มี merge commits ที่ไม่จำเป็น
- **Linear History**: Git history เป็นเส้นตรง ง่ายต่อการอ่าน
- **Easy to Debug**: ง่ายต่อการ track changes
- **Better for Code Review**: เห็นการเปลี่ยนแปลงได้ชัดเจน

### 7. ข้อควรระวัง

- **Force Push**: อาจต้องใช้ `--force-with-lease` หลัง rebase
- **Shared Branches**: อย่า rebase บน shared branches
- **Backup**: ควร backup ก่อน rebase เสมอ

### 8. Best Practices

1. **Rebase ก่อน Push**: `git pull --rebase` ก่อน push เสมอ
2. **Small Commits**: ทำ commit เล็กๆ หลายครั้ง
3. **Clear Messages**: เขียน commit message ให้ชัดเจน
4. **Test ก่อน Push**: ทดสอบ code ก่อน push
5. **Review ก่อน Merge**: ใช้ code review process

### 9. Troubleshooting

#### ถ้า Rebase ผิดพลาด
```bash
# ดูสถานะ
git status

# ยกเลิก rebase
git rebase --abort

# หรือ continue ถ้าแก้ไขแล้ว
git rebase --continue
```

#### ถ้า Force Push ไม่ได้
```bash
# ใช้ --force-with-lease แทน --force
git push --force-with-lease origin feature-branch
```

#### ถ้า Remote มี changes ใหม่
```bash
# Fetch latest changes
git fetch origin

# Rebase กับ remote
git rebase origin/main
```

## สรุป

Rebase workflow ช่วยให้ Git history สะอาดและง่ายต่อการจัดการ แต่ต้องระวังเรื่อง force push และ shared branches
