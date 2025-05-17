#!/usr/bin/env python

"""
Direct fix for adding the 'bio' column to the UserProfile table
"""

import os
import django
import pymysql
import getpass

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bawabati.settings')
django.setup()

def add_bio_column():
    print("=== Adding bio column to UserProfile table ===")
    
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
            # Check if column exists
            cursor.execute("SHOW COLUMNS FROM bawabati_app_userprofile LIKE 'bio'")
            if cursor.fetchone():
                print("✓ bio column already exists")
            else:
                # Add the bio column
                cursor.execute("ALTER TABLE bawabati_app_userprofile ADD COLUMN bio TEXT NULL")
                connection.commit()
                print("✓ bio column added successfully")
        
        # Get all tables
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [list(table.values())[0] for table in cursor.fetchall()]
            print(f"\nDatabase contains {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")
                
        # Check UserProfile columns
        with connection.cursor() as cursor:
            cursor.execute("DESCRIBE bawabati_app_userprofile")
            columns = cursor.fetchall()
            print(f"\nUserProfile columns:")
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
    add_bio_column() 