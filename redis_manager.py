#!/usr/bin/env python3
"""
Redis Manager Script
สคริปต์สำหรับจัดการ Redis connection และ cache
"""

import os
import sys
import redis
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.development')
import django
django.setup()

from django.conf import settings
from django.core.cache import cache


class RedisManager:
    """จัดการ Redis connection และ cache"""
    
    def __init__(self):
        self.redis_client = None
        self.connect()
    
    def connect(self):
        """เชื่อมต่อ Redis"""
        try:
            # ใช้การตั้งค่าจาก Django settings
            redis_url = getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379/1')
            self.redis_client = redis.from_url(redis_url)
            
            # ทดสอบการเชื่อมต่อ
            self.redis_client.ping()
            print("✅ เชื่อมต่อ Redis สำเร็จ!")
            return True
            
        except redis.ConnectionError as e:
            print(f"❌ ไม่สามารถเชื่อมต่อ Redis: {e}")
            print("🔧 กำลังพยายามเริ่ม Redis service...")
            return False
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")
            return False
    
    def test_connection(self):
        """ทดสอบการเชื่อมต่อ Redis"""
        try:
            if self.redis_client:
                result = self.redis_client.ping()
                print(f"✅ Redis Ping: {result}")
                return True
            else:
                print("❌ Redis client ไม่ได้เชื่อมต่อ")
                return False
        except Exception as e:
            print(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def get_info(self):
        """แสดงข้อมูล Redis"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                print("📊 ข้อมูล Redis:")
                print("=" * 40)
                print(f"Version: {info.get('redis_version', 'Unknown')}")
                print(f"Mode: {info.get('redis_mode', 'Unknown')}")
                print(f"Uptime: {info.get('uptime_in_seconds', 0)} seconds")
                print(f"Connected Clients: {info.get('connected_clients', 0)}")
                print(f"Used Memory: {info.get('used_memory_human', 'Unknown')}")
                print(f"Total Commands: {info.get('total_commands_processed', 0)}")
                return True
            else:
                print("❌ Redis client ไม่ได้เชื่อมต่อ")
                return False
        except Exception as e:
            print(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def test_cache(self):
        """ทดสอบ Django cache"""
        try:
            # ทดสอบการเขียน cache
            test_key = 'test_key'
            test_value = f'Test value at {datetime.now()}'
            
            cache.set(test_key, test_value, 30)  # 30 วินาที
            print(f"✅ เขียน cache: {test_key}")
            
            # ทดสอบการอ่าน cache
            cached_value = cache.get(test_key)
            if cached_value:
                print(f"✅ อ่าน cache: {cached_value}")
                return True
            else:
                print("❌ ไม่สามารถอ่าน cache ได้")
                return False
                
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการทดสอบ cache: {e}")
            return False
    
    def clear_cache(self):
        """ล้าง cache ทั้งหมด"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
                print("✅ ล้าง cache ทั้งหมดเรียบร้อย")
                return True
            else:
                print("❌ Redis client ไม่ได้เชื่อมต่อ")
                return False
        except Exception as e:
            print(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def show_keys(self):
        """แสดง keys ทั้งหมดใน Redis"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys('*')
                if keys:
                    print(f"🔑 Keys ใน Redis ({len(keys)} keys):")
                    print("=" * 40)
                    for key in keys[:20]:  # แสดงแค่ 20 keys แรก
                        key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                        ttl = self.redis_client.ttl(key)
                        print(f"  {key_str} (TTL: {ttl}s)")
                    
                    if len(keys) > 20:
                        print(f"  ... และอีก {len(keys) - 20} keys")
                else:
                    print("📭 ไม่มี keys ใน Redis")
                return True
            else:
                print("❌ Redis client ไม่ได้เชื่อมต่อ")
                return False
        except Exception as e:
            print(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def start_redis_service(self):
        """เริ่ม Redis service"""
        try:
            import subprocess
            result = subprocess.run(['brew', 'services', 'start', 'redis'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ เริ่ม Redis service สำเร็จ")
                time.sleep(2)  # รอให้ service เริ่ม
                return self.connect()
            else:
                print(f"❌ ไม่สามารถเริ่ม Redis service: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ ข้อผิดพลาด: {e}")
            return False
    
    def interactive_mode(self):
        """โหมด Interactive"""
        print("\n🎮 โหมด Interactive - Redis Manager")
        print("=" * 50)
        
        while True:
            print("\nเลือกคำสั่ง:")
            print("1. ทดสอบการเชื่อมต่อ")
            print("2. แสดงข้อมูล Redis")
            print("3. ทดสอบ Django Cache")
            print("4. แสดง Keys ทั้งหมด")
            print("5. ล้าง Cache ทั้งหมด")
            print("6. เริ่ม Redis Service")
            print("7. ออกจากโปรแกรม")
            
            choice = input("\nกรุณาเลือก (1-7): ").strip()
            
            if choice == '1':
                self.test_connection()
            elif choice == '2':
                self.get_info()
            elif choice == '3':
                self.test_cache()
            elif choice == '4':
                self.show_keys()
            elif choice == '5':
                confirm = input("ยืนยันการล้าง cache ทั้งหมด? (y/N): ").strip().lower()
                if confirm == 'y':
                    self.clear_cache()
            elif choice == '6':
                self.start_redis_service()
            elif choice == '7':
                print("👋 ขอบคุณที่ใช้งาน!")
                break
            else:
                print("❌ กรุณาเลือกตัวเลข 1-7")


def main():
    """ฟังก์ชันหลัก"""
    print("🚀 Redis Manager Script")
    print("=" * 30)
    
    try:
        manager = RedisManager()
        
        # ทดสอบการเชื่อมต่อ
        if manager.test_connection():
            print("✅ Redis พร้อมใช้งาน!")
        else:
            print("⚠️ Redis ไม่พร้อมใช้งาน")
        
        # รันโหมด Interactive
        manager.interactive_mode()
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
