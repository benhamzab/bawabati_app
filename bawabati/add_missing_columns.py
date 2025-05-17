#!/usr/bin/env python

"""
Fix missing columns in UserProfile table
"""

import os
import django
import pymysql
import getpass

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bawabati.settings')
django.setup()

def add_missing_columns():
    print("=== Adding missing columns to UserProfile table ===")
    
    # Get MySQL password
    print("\nEnter your MySQL root password:")
    mysql_password = getpass.getpass()
    
    try:
        # Connect to MySQL
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=mysql_password,
            database='bawabati_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Check UserProfile columns
            cursor.execute("DESCRIBE bawabati_app_userprofile")
            columns = {column['Field']: column for column in cursor.fetchall()}
            
            # Check and add bio column
            if 'bio' not in columns:
                cursor.execute("ALTER TABLE bawabati_app_userprofile ADD COLUMN bio TEXT NULL")
                connection.commit()
                print("✓ Added bio column")
            else:
                print("✓ bio column already exists")
            
            # Check and add phone_number column
            if 'phone_number' not in columns:
                cursor.execute("ALTER TABLE bawabati_app_userprofile ADD COLUMN phone_number VARCHAR(15) NULL")
                connection.commit()
                print("✓ Added phone_number column")
            else:
                print("✓ phone_number column already exists")
            
            # Check and add profile_picture column if not exists
            if 'profile_picture' not in columns:
                cursor.execute("ALTER TABLE bawabati_app_userprofile ADD COLUMN profile_picture VARCHAR(100) NULL")
                connection.commit()
                print("✓ Added profile_picture column")
            else:
                print("✓ profile_picture column already exists")
                
        # Show final schema
        with connection.cursor() as cursor:
            cursor.execute("DESCRIBE bawabati_app_userprofile")
            columns = cursor.fetchall()
            print(f"\nFinal UserProfile columns:")
            for column in columns:
                print(f"  - {column['Field']} ({column['Type']})")
        
        print("\n✅ Fix completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check:")
        print("1. MySQL is running")
        print("2. The database name is correct")
        print("3. Your password is correct")
        return False
    
    return True

if __name__ == "__main__":
    add_missing_columns() 