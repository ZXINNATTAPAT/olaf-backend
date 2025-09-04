#!/usr/bin/env python3
"""
User Management Script
สคริปต์สำหรับจัดการผู้ใช้และรหัสผ่าน
"""

import os
import sys
import django
from getpass import getpass

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.development')
django.setup()

from authentication.models import Account
from django.contrib.auth import authenticate


class UserManager:
    """จัดการผู้ใช้และรหัสผ่าน"""
    
    def __init__(self):
        self.admin_email = 'admin@example.com'
    
    def show_admin_info(self):
        """แสดงข้อมูล admin user"""
        try:
            admin = Account.objects.get(email=self.admin_email)
            print("👤 ข้อมูล Admin User:")
            print("=" * 40)
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"First Name: {admin.first_name}")
            print(f"Last Name: {admin.last_name}")
            print(f"Is Active: {admin.is_active}")
            print(f"Is Staff: {admin.is_staff}")
            print(f"Is Superuser: {admin.is_superuser}")
            print(f"Last Login: {admin.last_login or 'ไม่เคยล็อกอิน'}")
            print(f"Created At: {admin.created_at}")
            print(f"Password Set: {'✅ มี' if admin.password else '❌ ไม่มี'}")
            
        except Account.DoesNotExist:
            print("❌ ไม่พบ admin user")
    
    def test_password(self, password):
        """ทดสอบรหัสผ่าน"""
        try:
            admin = Account.objects.get(email=self.admin_email)
            if admin.check_password(password):
                print(f"✅ รหัสผ่านถูกต้อง: {password}")
                return True
            else:
                print(f"❌ รหัสผ่านไม่ถูกต้อง: {password}")
                return False
        except Account.DoesNotExist:
            print("❌ ไม่พบ admin user")
            return False
    
    def set_password(self, new_password):
        """ตั้งรหัสผ่านใหม่"""
        try:
            admin = Account.objects.get(email=self.admin_email)
            admin.set_password(new_password)
            admin.save()
            print(f"✅ ตั้งรหัสผ่านใหม่เรียบร้อย: {new_password}")
            return True
        except Account.DoesNotExist:
            print("❌ ไม่พบ admin user")
            return False
    
    def create_admin(self):
        """สร้าง admin user ใหม่"""
        try:
            admin = Account.objects.create_user(
                username='admin',
                email=self.admin_email,
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True
            )
            print("✅ สร้าง admin user ใหม่เรียบร้อย")
            print(f"🔐 รหัสผ่านเริ่มต้น: admin123")
            return True
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            return False
    
    def list_all_users(self):
        """แสดงรายการผู้ใช้ทั้งหมด"""
        users = Account.objects.all()
        print(f"\n👥 รายการผู้ใช้ทั้งหมด ({users.count()} คน):")
        print("=" * 60)
        print(f"{'ID':<3} {'Username':<15} {'Email':<25} {'Staff':<5} {'Active':<6}")
        print("-" * 60)
        
        for user in users:
            print(f"{user.id:<3} {user.username:<15} {user.email:<25} {'✅' if user.is_staff else '❌':<5} {'✅' if user.is_active else '❌':<6}")
    
    def interactive_mode(self):
        """โหมด Interactive"""
        print("\n🎮 โหมด Interactive - User Management")
        print("=" * 50)
        
        while True:
            print("\nเลือกคำสั่ง:")
            print("1. แสดงข้อมูล admin")
            print("2. ทดสอบรหัสผ่าน")
            print("3. ตั้งรหัสผ่านใหม่")
            print("4. สร้าง admin user ใหม่")
            print("5. แสดงรายการผู้ใช้ทั้งหมด")
            print("6. ออกจากโปรแกรม")
            
            choice = input("\nกรุณาเลือก (1-6): ").strip()
            
            if choice == '1':
                self.show_admin_info()
            elif choice == '2':
                password = getpass("กรุณาใส่รหัสผ่าน: ")
                self.test_password(password)
            elif choice == '3':
                new_password = getpass("รหัสผ่านใหม่: ")
                confirm_password = getpass("ยืนยันรหัสผ่าน: ")
                if new_password == confirm_password:
                    self.set_password(new_password)
                else:
                    print("❌ รหัสผ่านไม่ตรงกัน")
            elif choice == '4':
                confirm = input("ยืนยันการสร้าง admin user ใหม่? (y/N): ").strip().lower()
                if confirm == 'y':
                    self.create_admin()
            elif choice == '5':
                self.list_all_users()
            elif choice == '6':
                print("👋 ขอบคุณที่ใช้งาน!")
                break
            else:
                print("❌ กรุณาเลือกตัวเลข 1-6")


def main():
    """ฟังก์ชันหลัก"""
    print("🚀 User Management Script")
    print("=" * 30)
    
    try:
        manager = UserManager()
        
        # แสดงข้อมูล admin ปัจจุบัน
        manager.show_admin_info()
        
        # รันโหมด Interactive
        manager.interactive_mode()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
