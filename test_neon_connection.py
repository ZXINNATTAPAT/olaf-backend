#!/usr/bin/env python3
"""
Test script to verify Neon database connection
"""
import os
import sys
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def test_neon_connection():
    """Test connection to Neon database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Successfully connected to Neon database!")
            print(f"📊 PostgreSQL version: {version[0]}")
            
            # Test creating a simple table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert test data
            cursor.execute("""
                INSERT INTO test_connection (message) 
                VALUES ('Hello from Neon!') 
                ON CONFLICT DO NOTHING;
            """)
            
            # Query test data
            cursor.execute("SELECT * FROM test_connection;")
            result = cursor.fetchone()
            print(f"📝 Test data: {result}")
            
            # Clean up
            cursor.execute("DROP TABLE IF EXISTS test_connection;")
            
            print("🎉 Neon database connection test completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error connecting to Neon database: {e}")
        return False

if __name__ == "__main__":
    print("🔗 Testing Neon database connection...")
    
    # Check if using connection string or individual parameters
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"🔗 Using connection string: {database_url[:50]}...")
    else:
        print(f"📍 Host: {os.getenv('DB_HOST', 'Not set')}")
        print(f"🗄️  Database: {os.getenv('DB_NAME', 'Not set')}")
        print(f"👤 User: {os.getenv('DB_USER', 'Not set')}")
    
    print("-" * 50)
    
    success = test_neon_connection()
    
    if success:
        print("\n✅ Ready to run migrations!")
        print("Run: python manage.py migrate")
    else:
        print("\n❌ Please check your Neon database credentials in .env file")
        print("Make sure you have:")
        print("- DB_NAME (your Neon database name)")
        print("- DB_USER (your Neon username)")  
        print("- DB_PASSWORD (your Neon password)")
        print("- DB_HOST (your Neon host)")
